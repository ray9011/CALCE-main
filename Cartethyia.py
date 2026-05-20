import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
from scipy.stats import linregress

def plot_resistance_stats_over_cycles(path_sorted):
    resistance_data_by_cycle = {}
    cycle_counter = 1

    for p in path_sorted:
        try:
            df = pd.read_excel(p, sheet_name=1)
            if 'Cycle_Index' not in df.columns or 'Internal_Resistance(Ohm)' not in df.columns:
                continue

            file_cycles = sorted(set(df['Cycle_Index'].dropna()))
            for cycle in file_cycles:
                values = df[(df['Cycle_Index'] == cycle) & (df['Current(A)'] < 0)]['Internal_Resistance(Ohm)'].dropna().values
                if len(values) > 0:
                    resistance_data_by_cycle[cycle_counter] = values
                    cycle_counter += 1

        except Exception as e:
            print(f"錯誤讀取檔案 {p}: {e}")

    # 計算內阻特徵
    cycles_sorted = sorted(resistance_data_by_cycle.keys())
    R_mean = [np.mean(resistance_data_by_cycle[c]) for c in cycles_sorted]
    R_max = [np.max(resistance_data_by_cycle[c]) for c in cycles_sorted]
    R_min = [np.min(resistance_data_by_cycle[c]) for c in cycles_sorted]
    R_std = [np.std(resistance_data_by_cycle[c]) for c in cycles_sorted]
    R_range = [rmax - rmin for rmax, rmin in zip(R_max, R_min)]
    R_median = [np.median(resistance_data_by_cycle[c]) for c in cycles_sorted]

    print(f"所有檔案的 Cycle_Index 總長度: {len(cycles_sorted)}")

    # 畫圖：6 個特徵，2 列 3 行呈現
    metrics = [
        (R_mean, 'Mean Resistance', 'blue', 'Mean (Ohm)'),
        (R_max, 'Max Resistance', 'green', 'Max (Ohm)'),
        (R_min, 'Min Resistance', 'red', 'Min (Ohm)'),
        (R_std, 'Resistance Std Dev', 'purple', 'Std (Ohm)'),
        (R_range, 'Resistance Range', 'orange', 'Range (Ohm)'),
        (R_median, 'Resistance Median', 'brown', 'Median (Ohm)')
    ]

    fig, axs = plt.subplots(2, 3, figsize=(18, 10))
    fig.suptitle('Resistance Feature Plots (2x3)', fontsize=18)

    for ax, (data, title, color, ylabel) in zip(axs.flat, metrics):
        ax.scatter(cycles_sorted, data, label=title, color=color, s=30)
        ax.set_xlabel('Cycle Index')
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.grid(True)
        ax.legend()

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.show()

    # 回傳 dataframe（只含 6 個特徵）
    return pd.DataFrame({
        'cycle': cycles_sorted,
        'resistance_mean': R_mean,
        'resistance_max': R_max,
        'resistance_min': R_min,
        'resistance_std': R_std,
        'resistance_range': R_range,
        'resistance_median': R_median
    })
