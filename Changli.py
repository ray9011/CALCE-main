import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
import matplotlib.ticker as ticker
from scipy.stats import skew, kurtosis  
import matplotlib.pyplot as plt

def plot_current_stats_over_cycles(path_sorted):
    current_data_by_cycle = {}
    cycle_counter = 1  # 全域 cycle 累加器

    for p in path_sorted:
        try:
            df = pd.read_excel(p, sheet_name=1)
            if 'Cycle_Index' not in df.columns or 'Current(A)' not in df.columns:
                continue

            file_cycles = sorted(set(df['Cycle_Index'].dropna()))
            for cycle in file_cycles:
                currents = df[(df['Cycle_Index'] == cycle) & (df['Current(A)'] < 0)]['Current(A)'].dropna().values
                if len(currents) > 0:
                    current_data_by_cycle[cycle_counter] = currents
                    cycle_counter += 1

        except Exception as e:
            print(f"錯誤讀取檔案 {p}: {e}")

    # 電流特徵(平均值、最大值、最小值、標準差、範圍、中位數、偏度、峰度)
    cycles_sorted = sorted(current_data_by_cycle.keys())
    avg_current = [np.mean(current_data_by_cycle[c]) for c in cycles_sorted]
    max_current = [np.max(current_data_by_cycle[c]) for c in cycles_sorted]
    min_current = [np.min(current_data_by_cycle[c]) for c in cycles_sorted]
    std_current = [np.std(current_data_by_cycle[c]) for c in cycles_sorted]
    range_current = [np.max(current_data_by_cycle[c]) - np.min(current_data_by_cycle[c]) for c in cycles_sorted]
    median_current = [np.median(current_data_by_cycle[c]) for c in cycles_sorted]
    skew_current = [skew(current_data_by_cycle[c]) for c in cycles_sorted]
    kurtosis_current = [kurtosis(current_data_by_cycle[c]) for c in cycles_sorted]

    print(f"所有檔案的 Cycle_Index 總長度: {len(cycles_sorted)}")

    metrics = [
        (avg_current, 'Mean Current', 'blue', 'Mean Current (A)'),
        (max_current, 'Max Current', 'green', 'Max Current (A)'),
        (min_current, 'Min Current', 'red', 'Min Current (A)'),
        (std_current, 'Current Std Dev', 'purple', 'Current Std Dev (A)'),
        (range_current, 'Current Range', 'orange', 'Current Range (A)'),
        (median_current, 'Current Median', 'brown', 'Current Median (A)'),
        (skew_current, 'Current Skewness', 'darkcyan', 'Skewness'),
        (kurtosis_current, 'Current Kurtosis', 'darkmagenta', 'Kurtosis'),
    ]

    for i in range(0, len(metrics), 4):
        fig, axs = plt.subplots(2, 2, figsize=(12, 8))
        fig.suptitle('Current Feature Plots', fontsize=16)
        
        for ax, (data, label, color, ylabel) in zip(axs.flat, metrics[i:i+4]):
            ax.scatter(cycles_sorted, data, label=label, color=color, s=30)
            ax.set_xlabel('Cycle Index')
            ax.set_ylabel(ylabel)
            ax.set_title(label)
            ax.grid(True)
            ax.legend()
        
        plt.tight_layout(rect=[0, 0, 1, 0.95])
        plt.show()

    return pd.DataFrame({
        'cycle': cycles_sorted,
        'current_mean': avg_current,
        'current_max': max_current,
        'current_min': min_current,
        'current_std': std_current,
        'current_range': range_current,
        'current_median': median_current,
        'current_skewness': skew_current,
        'current_kurtosis': kurtosis_current
    })
