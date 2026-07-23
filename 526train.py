import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from skimage.transform import resize
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader, ConcatDataset
from pathlib import Path
import csv
import gc 
import time

# ---------------- 參數與路徑設定 (已修正為 Experimental_Plots) ----------------
DATA6_ROOT = Path(r"C:/Users/王奕傑/Desktop/CALCE-main/data6")
# 輸出路徑修正
SAVE_FOLDER = Path(r"C:/Users/王奕傑/Desktop/Experimental_Plots")
MODEL_SAVE_FOLDER = SAVE_FOLDER / "models" 
SAVE_FOLDER.mkdir(parents=True, exist_ok=True)
MODEL_SAVE_FOLDER.mkdir(parents=True, exist_ok=True) 

# CSV 紀錄檔
CSV_LOG_PATH = SAVE_FOLDER / "capacity_experimental_results.csv"
SEQ_LEN = 8
EPS = 1e-12
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ---------------- 核心功能 (保持原樣) ----------------
def get_tm_matrix(feat_series, t_series, calc_bins=64, display_size=16, window=5):
    if len(feat_series) < 50:
        new_len = 100
        feat_series = np.interp(np.linspace(0, len(feat_series)-1, new_len), np.arange(len(feat_series)), feat_series)
        t_series = np.interp(np.linspace(0, len(t_series)-1, new_len), np.arange(len(t_series)), t_series)
    
    dfdt = np.diff(feat_series) / (np.diff(t_series) + EPS)
    dfdt = dfdt[np.isfinite(dfdt)]
    
    if len(dfdt) <= window: 
        return np.zeros((display_size, display_size), dtype=np.float32)
    
    bins = np.linspace(np.min(dfdt), np.max(dfdt), calc_bins + 1)
    digitized = (calc_bins - 1) - np.digitize(dfdt, bins[1:-1], right=True)
    
    W = np.zeros((calc_bins, calc_bins))
    for i in range(len(digitized) - window):
        for step in range(1, window + 1):
            W[digitized[i], digitized[i + step]] += 1
            
    W_resized = resize(W, (display_size, display_size), order=1, mode='constant')
    
    for col in range(display_size):
        for row in range(display_size):
            if col < row or row < (col - 3):
                W_resized[col, col] += W_resized[row, col]
                W_resized[row, col] = 0
                
    tm = W_resized / (W_resized.sum(axis=1, keepdims=True) + EPS)
    return tm.T.astype(np.float32)

class MarkovDataset(Dataset):
    def __init__(self, file_path, display_size=16):
        df = pd.read_csv(file_path)
        self.cycles = sorted(df['cycle'].unique())
        self.data_by_cycle = {c: df[df['cycle'] == c] for c in self.cycles}
        self.soh = {c: df[df['cycle'] == c]['SoH'].iloc[0] for c in self.cycles}
        self.display_size = display_size
        self.cache = {}
        
    def __len__(self): 
        return len(self.cycles) - SEQ_LEN + 1
        
    def __getitem__(self, idx):
        target_cycles = self.cycles[idx : idx + SEQ_LEN]
        imgs = []
        for c in target_cycles:
            if c not in self.cache:
                group = self.data_by_cycle[c]
                base = get_tm_matrix(group['Voltage[V]'].values, group['Times(s)'].values, display_size=self.display_size)
                self.cache[c] = base 
            imgs.append(torch.from_numpy(self.cache[c]).unsqueeze(0))
        return torch.stack(imgs), torch.tensor([self.soh[target_cycles[-1]]], dtype=torch.float32)

class Dynamic_CNN_LSTM(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv_net = nn.Sequential(
            nn.Conv2d(1, 32, 3, padding=1), nn.ReLU(),
            nn.Conv2d(32, 64, 3, padding=1), nn.ReLU(),
            nn.Conv2d(64, 128, 3, padding=1), nn.ReLU(),
            nn.AdaptiveAvgPool2d((1, 1)) 
        )
        self.lstm = nn.LSTM(128, 64, batch_first=True)
        self.head = nn.Linear(64, 1)
        
    def forward(self, x):
        B, T, C, H, W = x.shape
        features = self.conv_net(x.view(B*T, C, H, W)).view(B, T, 128)
        lstm_out, _ = self.lstm(features)
        return self.head(lstm_out[:, -1, :])

# ---------------- 主測試循環 (1 ~ 128) ----------------
if __name__ == "__main__":
    # 修改為 1 ~ 128 
    display_sizes = range(1, 129) 
    test_file = "CS2_38_SOH.csv"
    train_indices = [33, 34, 35, 36, 37]
    
    # 檢查 CSV 是否存在，不存在才寫表頭
    if not CSV_LOG_PATH.exists():
        with open(CSV_LOG_PATH, mode='w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(['s', 'RMSE', 'MAE', 'Time'])

    scaler = torch.cuda.amp.GradScaler()

    for s in display_sizes:
        print(f"\n>>> 執行狀態數 s = {s} (Float16 全面開啟) ...")
        s_start_time = time.perf_counter() 
        
        train_sets = [MarkovDataset(DATA6_ROOT / f"CS2_{i}_SOH.csv", display_size=s) for i in train_indices]
        loader = DataLoader(ConcatDataset(train_sets), batch_size=16, shuffle=True)
        ds_test = MarkovDataset(DATA6_ROOT / test_file, display_size=s)
        test_loader = DataLoader(ds_test, batch_size=1)

        model = Dynamic_CNN_LSTM().to(DEVICE)
        optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
        criterion = nn.MSELoss()

        # 訓練階段
        model.train()
        for epoch in range(10):
            for x, y in loader:
                x, y = x.to(DEVICE), y.to(DEVICE)
                optimizer.zero_grad()
                with torch.cuda.amp.autocast():
                    outputs = model(x)
                    loss = criterion(outputs, y)
                scaler.scale(loss).backward()
                scaler.step(optimizer)
                scaler.update()

        # 儲存權重
        torch.save(model.state_dict(), MODEL_SAVE_FOLDER / f"capacity_model_s{s}.pth")

        # 評估階段
        model.eval()
        cycles, y_true_list, y_pred_list = [], [], []
        with torch.no_grad():
            for i, (x, y) in enumerate(test_loader):
                cycles.append(ds_test.cycles[i + SEQ_LEN - 1])
                y_true_list.append(y.item())
                with torch.cuda.amp.autocast():
                    pred = model(x.to(DEVICE)).item()
                y_pred_list.append(pred)
        
        s_end_time = time.perf_counter()
        total_s_time = s_end_time - s_start_time 
        
        y_true = np.array(y_true_list)
        y_pred = np.array(y_pred_list)
        rmse = np.sqrt(np.mean((y_true - y_pred)**2))
        mae = np.mean(np.abs(y_true - y_pred))

        # 寫入結果 (Append 模式不覆蓋)
        with open(CSV_LOG_PATH, mode='a', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow([s, rmse, mae, f"{total_s_time:.2f}"])

        # 圖 A: Result_SOH_s{s}_2
        plt.figure(figsize=(10, 5))
        plt.plot(cycles, y_true, label='Actual SOH', color='black')
        plt.plot(cycles, y_pred, '--', label=f'Pred (s={s})', color='red')
        plt.title(f'SOH Prediction (States: {s})')
        plt.text(0.05, 0.05, f'RMSE: {rmse:.4f}\nMAE: {mae:.4f}\nTime: {total_s_time:.2f}s', 
                 transform=plt.gca().transAxes, bbox=dict(facecolor='white', alpha=0.7))
        plt.xlabel('Cycle'); plt.ylabel('SOH'); plt.legend()
        plt.savefig(SAVE_FOLDER / f"Result_SOH_s{s}_2.png")
        plt.close()

        # 圖 B: Result_Error
        plt.figure(figsize=(10, 5))
        plt.scatter(cycles, np.abs(y_true - y_pred), s=10, color='blue', alpha=0.5, label='Absolute Error')
        plt.axhline(y=rmse, color='orange', linestyle='--', label=f'RMSE Line: {rmse:.4f}')
        plt.axhline(y=mae, color='green', linestyle=':', label=f'MAE Line: {mae:.4f}')
        plt.title(f'Error Distribution (States: {s})')
        plt.xlabel('Cycle'); plt.ylabel('Absolute Error'); plt.legend(); plt.grid(axis='y', linestyle=':', alpha=0.6)
        plt.savefig(SAVE_FOLDER / f"Result_Error_s{s}.png")
        plt.close()

        # 記憶體清理
        del model, optimizer, loader, train_sets, ds_test, test_loader
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    # ---------------- 最終繪製總圖 (獨立兩張) ----------------
    df_results = pd.read_csv(CSV_LOG_PATH)
    
    # 總圖 1: RMSE
    plt.figure(figsize=(12, 6))
    plt.plot(df_results['s'], df_results['RMSE'], label='RMSE', color='blue', marker='o', markersize=2)
    plt.title('Overall RMSE vs. States')
    plt.xlabel('Number of Markov States (1 ~ 128)'); plt.ylabel('RMSE')
    plt.grid(True, linestyle='--', alpha=0.5); plt.legend(); plt.tight_layout()
    plt.savefig(SAVE_FOLDER / "Summary_RMSE_Curve.png", dpi=300)
    plt.close()

    # 總圖 2: MAE
    plt.figure(figsize=(12, 6))
    plt.plot(df_results['s'], df_results['MAE'], label='MAE', color='green', marker='x', markersize=2)
    plt.title('Overall MAE vs. States')
    plt.xlabel('Number of Markov States (1 ~ 128)'); plt.ylabel('MAE')
    plt.grid(True, linestyle='--', alpha=0.5); plt.legend(); plt.tight_layout()
    plt.savefig(SAVE_FOLDER / "Summary_MAE_Curve.png", dpi=300)
    plt.close()

    print(f"✨ 任務全數完成！結果已儲存至：{SAVE_FOLDER}")