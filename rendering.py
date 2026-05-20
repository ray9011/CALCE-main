import os
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

# -----------------------------
# 參數設定
# -----------------------------
csv_path = r"C:/Users/王奕傑/Desktop/CALCE-main/features_CS2_33.csv"
output_dir = r"C:/Users/王奕傑/Desktop/CALCE-main/output_3D"



# 確保輸出資料夾存在
os.makedirs(output_dir, exist_ok=True)

# -----------------------------
# 讀取 CSV
# -----------------------------
df = pd.read_csv(csv_path, header=0)  # 第一列是欄名，資料從第2列開始

# 假設 CSV 第一列是標題，之後每列是特徵名稱
# 取第一列（row 0）、從第2欄開始（column 1 到最後）
cycle_row = df.iloc[0, 1:].astype(float)      # 第一列是 cycle
capacity_row = df.iloc[1, 1:].astype(float)   # 第二列是 capacity
voltage_row = df.iloc[2, 1:].astype(float)    # 第三列是 voltage_mean

# -----------------------------
# 生成 3D 圖
# -----------------------------
for i in range(len(cycle_row)):
    fig = plt.figure(figsize=(8,6))
    ax = fig.add_subplot(111, projection='3d')

    # 畫線圖：X=cycle, Y=capacity, Z=voltage
    ax.plot([cycle_row.iloc[i]], [capacity_row.iloc[i]], [voltage_row.iloc[i]], marker='o', markersize=6, color='b')

    ax.set_xlabel('Cycle')
    ax.set_ylabel('Capacity (Ah)')
    ax.set_zlabel('Voltage_mean (V)')
    ax.set_title(f'3D View - Cycle {i+1}')

    # 設定視角 (可以調整)
    ax.view_init(elev=30, azim=120)

    # 儲存圖片
    output_file = os.path.join(output_dir, f'cycle_{i+1}.png')
    plt.savefig(output_file)
    plt.close(fig)

print(f"完成！所有圖片已保存到 {output_dir}")
