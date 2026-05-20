import numpy as np
import pandas as pd
from scipy.stats import skew, kurtosis
import matplotlib.pyplot as plt

def plot_current_diff_stats_over_cycles(path_sorted):
    current_diff_by_cycle = {}
    cycle_counter = 1

    for p in path_sorted:
        try:
            df = pd.read_excel(p, sheet_name=1)
            if not all(col in df.columns for col in ['Cycle_Index', 'Current(A)', 'Test_Time(s)']):
                print(f"跳過檔案：{p}，缺少必要欄位")
                continue

            file_cycles = sorted(df['Cycle_Index'].dropna().unique())

            for cycle in file_cycles:
                cycle_data = df[(df['Cycle_Index'] == cycle) & (df['Current(A)'] < 0)]
                cycle_data = cycle_data.dropna(subset=['Current(A)', 'Test_Time(s)'])

                if len(cycle_data) < 2:
                    continue

                I = cycle_data['Current(A)'].values
                t = cycle_data['Test_Time(s)'].values

                dt = np.diff(t)
                dI = np.diff(I)

                valid = dt != 0
                if not np.any(valid):
                    continue

                dIdt = np.full(len(dt), np.nan)
                dIdt[valid] = dI[valid] / dt[valid]
                dIdt = dIdt[~np.isnan(dIdt)]

                if len(dIdt) > 0:
                    current_diff_by_cycle[cycle_counter] = dIdt
                    cycle_counter += 1
                    
        except Exception as e:
            print(f"錯誤處理檔案 {p}: {e}")

    cycles_sorted = sorted(current_diff_by_cycle.keys())

    # 建立每個特徵值的清單
    mean_diff = []
    max_diff = []
    min_diff = []
    std_diff = []
    range_diff = []
    median_diff = []
    skew_diff = []
    kurt_diff = []

    for c in cycles_sorted:
        vals = current_diff_by_cycle[c]
        mean_diff.append(np.mean(vals))
        max_diff.append(np.max(vals))
        min_diff.append(np.min(vals))
        std_diff.append(np.std(vals))
        range_diff.append(np.max(vals) - np.min(vals))
        median_diff.append(np.median(vals))
        skew_diff.append(skew(vals) if len(vals) > 2 else np.nan)
        kurt_diff.append(kurtosis(vals) if len(vals) > 3 else np.nan)

    print(f"共處理 {len(cycles_sorted)} 個循環的微分特徵")

    # 繪圖（可選）
    metrics = [
        (mean_diff, 'Mean dI/dt', 'blue', 'Mean (A/s)'),
        (max_diff, 'Max dI/dt', 'green', 'Max (A/s)'),
        (min_diff, 'Min dI/dt', 'red', 'Min (A/s)'),
        (std_diff, 'Std Dev dI/dt', 'purple', 'Std Dev (A/s)'),
        (range_diff, 'Range dI/dt', 'orange', 'Range (A/s)'),
        (median_diff, 'Median dI/dt', 'brown', 'Median (A/s)'),
        (skew_diff, 'Skewness dI/dt', 'darkcyan', 'Skewness'),
        (kurt_diff, 'Kurtosis dI/dt', 'darkmagenta', 'Kurtosis'),
    ]

    # 分成兩組，每組畫 4 張子圖
    for i in range(0, len(metrics), 4):
        fig, axs = plt.subplots(2, 2, figsize=(12, 8))
        fig.suptitle('dI/dt Feature Plots', fontsize=16)

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
        'didt_mean': mean_diff,
        'didt_max': max_diff,
        'didt_min': min_diff,
        'didt_std': std_diff,
        'didt_range': range_diff,
        'didt_median': median_diff,
        'didt_skewness': skew_diff,
        'didt_kurtosis': kurt_diff
    })


