import os
import pandas as pd
import matplotlib.pyplot as plt

def process_channel_file(file_path):
    try:
        df = pd.read_excel(file_path, sheet_name="Channel_1-006")
    except Exception as e:
        print(f" 無法讀取 {file_path}: {e}")
        return None

    if 'Cycle_Index' not in df.columns or 'Voltage(V)' not in df.columns:
        print(f" 檔案 {file_path} 缺少必要欄位")
        return None

    # ➤ 對每個 Cycle 做統計
    features = df.groupby('Cycle_Index')['Voltage(V)'].agg(['mean', 'std', 'max', 'min'])

    # ➤ 重新命名欄位為清楚的名稱
    features.rename(columns={
        'mean': 'Voltage_Mean',
        'std': 'Voltage_Std',
        'max': 'Voltage_Max',
        'min': 'Voltage_Min'
    }, inplace=True)

    return features

def plot_voltage_features(all_features):
    if not all_features:
        print(" 沒有找到有效的電壓特徵資料")
        return

    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    feature_keys = ['Voltage_Mean', 'Voltage_Std', 'Voltage_Max', 'Voltage_Min']
    titles = ['Mean Voltage (V)', 'Standard Deviation of Voltage (V)', 'Maximum Voltage (V)', 'Minimum Voltage (V)']
    axes = axes.flatten()

    for idx, (feature, title) in enumerate(zip(feature_keys, titles)):
        ax = axes[idx]
        for name, df in all_features.items():
            if feature in df.columns:
                ax.plot(df.index, df[feature], label=name.replace(".xlsx", ""))
        ax.set_title(title)
        ax.set_xlabel("Cycle Index")
        ax.set_ylabel("Voltage (V)")
        ax.legend()
        ax.grid(True)

    plt.tight_layout()
    plt.suptitle("Voltage Health Features (All Files)", fontsize=16, y=1.02)
    plt.show()

def process_all_files_in_directory(directory_path):
    all_features = {}

    for filename in os.listdir(directory_path):
        # ➤ 濾掉 Excel 的暫存檔（以 ~$ 開頭）
        if filename.endswith(".xlsx") and not filename.startswith("~$"):
            file_path = os.path.join(directory_path, filename)
            features = process_channel_file(file_path)
            if features is not None:
                all_features[filename] = features

    plot_voltage_features(all_features)
