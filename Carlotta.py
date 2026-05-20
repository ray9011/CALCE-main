import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import skew, kurtosis

def plot_voltage_diff_stats_over_cycles(path_sorted):
    dvdt_data_by_cycle = {}
    cycle_counter = 1  # 全域 cycle 累加器

    for p in path_sorted:
        try:
            df = pd.read_excel(p, sheet_name=1)
            if 'Cycle_Index' not in df.columns or 'dV/dt(V/s)' not in df.columns:
                continue

            file_cycles = sorted(set(df['Cycle_Index'].dropna()))
            for cycle in file_cycles:
                dvdt_values = df[(df['Cycle_Index'] == cycle) & (df['Current(A)'] < 0)]['dV/dt(V/s)'].dropna().values
                if len(dvdt_values) > 0:
                    dvdt_data_by_cycle[cycle_counter] = dvdt_values
                    cycle_counter += 1

        except Exception as e:
            print(f"錯誤讀取檔案 {p}: {e}")

    # 計算 dV/dt 統計特徵
    cycles_sorted = sorted(dvdt_data_by_cycle.keys())
    avg_dvdt = [np.mean(dvdt_data_by_cycle[c]) for c in cycles_sorted]
    max_dvdt = [np.max(dvdt_data_by_cycle[c]) for c in cycles_sorted]
    min_dvdt = [np.min(dvdt_data_by_cycle[c]) for c in cycles_sorted]
    std_dvdt = [np.std(dvdt_data_by_cycle[c]) for c in cycles_sorted]
    range_dvdt = [np.max(dvdt_data_by_cycle[c]) - np.min(dvdt_data_by_cycle[c]) for c in cycles_sorted]
    median_dvdt = [np.median(dvdt_data_by_cycle[c]) for c in cycles_sorted]
    skew_dvdt = [skew(dvdt_data_by_cycle[c]) for c in cycles_sorted]
    kurtosis_dvdt = [kurtosis(dvdt_data_by_cycle[c]) for c in cycles_sorted]

    print(f"所有檔案的 Cycle_Index 總長度: {len(cycles_sorted)}")

    # 整理資料與標籤
    metrics = [
        (avg_dvdt, 'Mean dV/dt', 'blue', 'Mean (V/s)'),
        (max_dvdt, 'Max dV/dt', 'green', 'Max (V/s)'),
        (min_dvdt, 'Min dV/dt', 'red', 'Min (V/s)'),
        (std_dvdt, 'Std Dev dV/dt', 'purple', 'Std Dev (V/s)'),
        (range_dvdt, 'Range dV/dt', 'orange', 'Range (V/s)'),
        (median_dvdt, 'Median dV/dt', 'brown', 'Median (V/s)'),
        (skew_dvdt, 'Skewness dV/dt', 'darkcyan', 'Skewness'),
        (kurtosis_dvdt, 'Kurtosis dV/dt', 'darkmagenta', 'Kurtosis'),
    ]

    # 分成兩組，每組 4 張子圖
    for i in range(0, len(metrics), 4):
        fig, axs = plt.subplots(2, 2, figsize=(12, 8))
        fig.suptitle('dV/dt Feature Plots', fontsize=16)

        for ax, (data, label, color, ylabel) in zip(axs.flat, metrics[i:i+4]):
            ax.scatter(cycles_sorted, data, label=label, color=color, s=30)
            ax.set_xlabel('Cycle Index')
            ax.set_ylabel(ylabel)
            ax.set_title(label)
            ax.grid(True)
            ax.legend()

        plt.tight_layout(rect=[0, 0, 1, 0.95])
        plt.show()

    # 回傳 DataFrame
    return pd.DataFrame({
        'cycle': cycles_sorted,
        'dvdt_mean': avg_dvdt,
        'dvdt_max': max_dvdt,
        'dvdt_min': min_dvdt,
        'dvdt_std': std_dvdt,
        'dvdt_range': range_dvdt,
        'dvdt_median': median_dvdt,
        'dvdt_skewness': skew_dvdt,
        'dvdt_kurtosis': kurtosis_dvdt
    })
