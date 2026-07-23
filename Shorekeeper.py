import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

# 這個函數會計算每個cycle的Discharge Capacity(Ah)平均值，並畫出隨著Cycle_Index的變化
def plot_discharge_capacity_over_cycles(path_sorted):
    discharge_capacity_data_by_cycle = {}

    # 遍歷所有檔案
    for p in path_sorted:
        try:
            # 讀取 Excel 檔案的第二個 sheet（索引為 1）
            df = pd.read_excel(p, sheet_name=1)

            # 檢查欄位是否包含 'Cycle_Index' 與 'Discharge_Capacity(Ah)'
            if 'Cycle_Index' not in df.columns or 'Discharge_Capacity(Ah)' not in df.columns:
                print(f"檔案 {p} 缺少必要欄位，跳過")
                continue

            # 依照Cycle_Index將Discharge_Capacity(Ah)資料收集
            for _, row in df.iterrows():
                cycle = row['Cycle_Index']
                discharge_capacity = row['Discharge_Capacity(Ah)']
                if pd.notna(cycle) and pd.notna(discharge_capacity):  # 避免 NaN
                    discharge_capacity_data_by_cycle.setdefault(cycle, []).append(discharge_capacity)

        except Exception as e:
            print(f"錯誤讀取檔案 {p}: {e}")

    # 計算每個cycle的Discharge Capacity(Ah)平均值
    avg_discharge_capacity_by_cycle = []
    cycles_sorted = sorted(discharge_capacity_data_by_cycle.keys())  # 按照cycle排序

    for cycle in cycles_sorted:
        capacities = discharge_capacity_data_by_cycle[cycle]
        avg_capacity = np.mean(capacities)  # 計算平均值
        avg_discharge_capacity_by_cycle.append(avg_capacity)

    # 畫圖
    plt.figure(figsize=(10, 6))
    plt.scatter(cycles_sorted, avg_discharge_capacity_by_cycle, label='Average Discharge Capacity', color='purple')

    plt.xlabel('Cycle Index', fontsize=14)
    plt.ylabel('Discharge Capacity (Ah)', fontsize=14)
    plt.title('Average Discharge Capacity Over Cycles', fontsize=16)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    # 強制 Y 軸顯示完整的六位小數，不再用科學記號
    plt.gca().yaxis.set_major_formatter(ticker.FormatStrFormatter('%.6f'))

    plt.show()
