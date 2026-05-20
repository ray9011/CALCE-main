import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
import matplotlib.ticker as ticker
from scipy.stats import skew, kurtosis  
import matplotlib.pyplot as plt

def plot_voltage_stats_over_cycles(path_sorted):
    voltage_data_by_cycle = {}
    cycle_counter = 1  # 全域 cycle 累加器

    for p in path_sorted:
        try:
            df = pd.read_excel(p, sheet_name=1)
            if 'Cycle_Index' not in df.columns or 'Voltage(V)' not in df.columns:
                continue

            file_cycles = sorted(set(df['Cycle_Index'].dropna()))
            for cycle in file_cycles:
                voltages = df[(df['Cycle_Index'] == cycle) & (df['Current(A)'] < 0)]['Voltage(V)'].dropna().values
                if len(voltages) > 0:
                    voltage_data_by_cycle[cycle_counter] = voltages
                    cycle_counter += 1

        except Exception as e:
            print(f"錯誤讀取檔案 {p}: {e}")

    # 電壓特徵(平均值、最大值、最小值、標準差、範圍、中位數、偏度、峰度)
    cycles_sorted = sorted(voltage_data_by_cycle.keys())
    avg_voltage = [np.mean(voltage_data_by_cycle[c]) for c in cycles_sorted]
    max_voltage = [np.max(voltage_data_by_cycle[c]) for c in cycles_sorted]
    min_voltage = [np.min(voltage_data_by_cycle[c]) for c in cycles_sorted]
    std_voltage = [np.std(voltage_data_by_cycle[c]) for c in cycles_sorted]
    range_voltage = [np.max(voltage_data_by_cycle[c]) - np.min(voltage_data_by_cycle[c]) for c in cycles_sorted]
    median_voltage = [np.median(voltage_data_by_cycle[c]) for c in cycles_sorted]
    skew_voltage = [skew(voltage_data_by_cycle[c]) for c in cycles_sorted]
    kurtosis_voltage = [kurtosis(voltage_data_by_cycle[c]) for c in cycles_sorted]
    
    # 整理資料與標籤
    metrics = [
        (avg_voltage, 'Mean Voltage', 'blue', 'Mean Voltage (V)'),
        (max_voltage, 'Max Voltage', 'green', 'Max Voltage (V)'),
        (min_voltage, 'Min Voltage', 'red', 'Min Voltage (V)'),
        (std_voltage, 'Voltage Std Dev', 'purple', 'Voltage Std Dev (V)'),
        (range_voltage, 'Voltage Range', 'orange', 'Voltage Range (V)'),
        (median_voltage, 'Voltage Median', 'brown', 'Voltage Median (V)'),
        (skew_voltage, 'Voltage Skewness', 'darkcyan', 'Skewness'),
        (kurtosis_voltage, 'Voltage Kurtosis', 'darkmagenta', 'Kurtosis'),
    ]

    # 分成兩組，每組 4 張子圖
    for i in range(0, len(metrics), 4):
        fig, axs = plt.subplots(2, 2, figsize=(12, 8))
        fig.suptitle('Voltage Feature Plots', fontsize=16)
        
        for ax, (data, label, color, ylabel) in zip(axs.flat, metrics[i:i+4]):
            ax.scatter(cycles_sorted, data, label=label, color=color, s=30)
            ax.set_xlabel('Cycle Index')
            ax.set_ylabel(ylabel)
            ax.set_title(label)
            ax.grid(True)
            ax.legend()
        
        plt.tight_layout(rect=[0, 0, 1, 0.95])  # 留空間給 suptitle
    plt.show()

    # ✅ 回傳 DataFrame
    return pd.DataFrame({
        'cycle': cycles_sorted,
        'voltage_mean': avg_voltage,
        'voltage_max': max_voltage,
        'voltage_min': min_voltage,
        'voltage_std': std_voltage,
        'voltage_range': range_voltage,
        'voltage_median': median_voltage,
        'voltage_skewness': skew_voltage,
        'voltage_kurtosis': kurtosis_voltage,
    })

# import matplotlib.pyplot as plt
# import numpy as np
# import pandas as pd
# import os
# import matplotlib.ticker as ticker
# from scipy.stats import skew, kurtosis  

# def plot_voltage_stats_over_cycles(path_sorted):
#     voltage_data_by_cycle = {}
#     plateau_duration_by_cycle = {}
#     cycle_counter = 1  # 全域 cycle 累加器

#     for p in path_sorted:
#         try:
#             df = pd.read_excel(p, sheet_name=1)
#             if 'Cycle_Index' not in df.columns or 'Voltage(V)' not in df.columns or 'Time(s)' not in df.columns:
#                 continue

#             file_cycles = sorted(set(df['Cycle_Index'].dropna()))
#             for cycle in file_cycles:
#                 # 電壓資料
#                 voltages = df[(df['Cycle_Index'] == cycle) & (df['Current(A)'] < 0)]['Voltage(V)'].dropna().values
#                 if len(voltages) > 0:
#                     voltage_data_by_cycle[cycle_counter] = voltages

#                     # 電壓平台資料
#                     time_series = df[(df['Cycle_Index'] == cycle) & (df['Current(A)'] < 0)][['Voltage(V)', 'Time(s)']].dropna()
#                     plateau_data = time_series[(time_series['Voltage(V)'] >= 3.7) & (time_series['Voltage(V)'] <= 3.9)]

#                     if not plateau_data.empty:
#                         duration = plateau_data['Time(s)'].max() - plateau_data['Time(s)'].min()
#                         plateau_duration_by_cycle[cycle_counter] = round(duration, 2)
#                     else:
#                         plateau_duration_by_cycle[cycle_counter] = 0.0

#                     cycle_counter += 1

#         except Exception as e:
#             print(f"錯誤讀取檔案 {p}: {e}")

#     # 電壓特徵計算
#     cycles_sorted = sorted(voltage_data_by_cycle.keys())
#     avg_voltage = [np.mean(voltage_data_by_cycle[c]) for c in cycles_sorted]
#     max_voltage = [np.max(voltage_data_by_cycle[c]) for c in cycles_sorted]
#     min_voltage = [np.min(voltage_data_by_cycle[c]) for c in cycles_sorted]
#     std_voltage = [np.std(voltage_data_by_cycle[c]) for c in cycles_sorted]
#     range_voltage = [np.max(voltage_data_by_cycle[c]) - np.min(voltage_data_by_cycle[c]) for c in cycles_sorted]
#     median_voltage = [np.median(voltage_data_by_cycle[c]) for c in cycles_sorted]
#     skew_voltage = [skew(voltage_data_by_cycle[c]) for c in cycles_sorted]
#     kurtosis_voltage = [kurtosis(voltage_data_by_cycle[c]) for c in cycles_sorted]
#     plateau_duration = [plateau_duration_by_cycle.get(c, 0.0) for c in cycles_sorted]

#     # 畫圖
#     metrics = [
#         (avg_voltage, 'Mean Voltage', 'blue', 'Mean Voltage (V)'),
#         (max_voltage, 'Max Voltage', 'green', 'Max Voltage (V)'),
#         (min_voltage, 'Min Voltage', 'red', 'Min Voltage (V)'),
#         (std_voltage, 'Voltage Std Dev', 'purple', 'Voltage Std Dev (V)'),
#         (range_voltage, 'Voltage Range', 'orange', 'Voltage Range (V)'),
#         (median_voltage, 'Voltage Median', 'brown', 'Voltage Median (V)'),
#         (skew_voltage, 'Voltage Skewness', 'darkcyan', 'Skewness'),
#         (kurtosis_voltage, 'Voltage Kurtosis', 'darkmagenta', 'Kurtosis'),
#     ]

#     for i in range(0, len(metrics), 4):
#         fig, axs = plt.subplots(2, 2, figsize=(12, 8))
#         fig.suptitle('Voltage Feature Plots', fontsize=16)
        
#         for ax, (data, label, color, ylabel) in zip(axs.flat, metrics[i:i+4]):
#             ax.scatter(cycles_sorted, data, label=label, color=color, s=30)
#             ax.set_xlabel('Cycle Index')
#             ax.set_ylabel(ylabel)
#             ax.set_title(label)
#             ax.grid(True)
#             ax.legend()
        
#         plt.tight_layout(rect=[0, 0, 1, 0.95])
#     plt.show()

#     # ✅ 回傳 DataFrame
#     return pd.DataFrame({
#         'cycle': cycles_sorted,
#         'voltage_mean': avg_voltage,
#         'voltage_max': max_voltage,
#         'voltage_min': min_voltage,
#         'voltage_std': std_voltage,
#         'voltage_range': range_voltage,
#         'voltage_median': median_voltage,
#         'voltage_skewness': skew_voltage,
#         'voltage_kurtosis': kurtosis_voltage,
#         'voltage_plateau_duration': plateau_duration
#     })
