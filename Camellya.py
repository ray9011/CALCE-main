import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import skew, kurtosis

def plot_energy_stats_over_cycles(path_sorted):
    energy_data_by_cycle = {}
    cycle_counter = 1

    for p in path_sorted:
        try:
            df = pd.read_excel(p, sheet_name=1)
            if 'Cycle_Index' not in df.columns or 'Discharge_Energy(Wh)' not in df.columns:
                continue

            file_cycles = sorted(set(df['Cycle_Index'].dropna()))
            for cycle in file_cycles:
                energies = df[df['Cycle_Index'] == cycle]['Discharge_Energy(Wh)'].dropna().values
                if len(energies) > 0:
                    energy_data_by_cycle[cycle_counter] = energies
                    cycle_counter += 1

        except Exception as e:
            print(f"錯誤讀取檔案 {p}: {e}")

    # 計算統計特徵
    cycles_sorted = sorted(energy_data_by_cycle.keys())
    avg_energy = [np.mean(energy_data_by_cycle[c]) for c in cycles_sorted]
    max_energy = [np.max(energy_data_by_cycle[c]) for c in cycles_sorted]
    min_energy = [np.min(energy_data_by_cycle[c]) for c in cycles_sorted]
    std_energy = [np.std(energy_data_by_cycle[c]) for c in cycles_sorted]
    range_energy = [np.max(energy_data_by_cycle[c]) - np.min(energy_data_by_cycle[c]) for c in cycles_sorted]
    median_energy = [np.median(energy_data_by_cycle[c]) for c in cycles_sorted]
    skew_energy = [skew(energy_data_by_cycle[c]) for c in cycles_sorted]
    kurtosis_energy = [kurtosis(energy_data_by_cycle[c]) for c in cycles_sorted]

    print(f"所有檔案的 Cycle_Index 總長度: {len(cycles_sorted)}")

    # 八個能量特徵可視化
    metrics = [
        (avg_energy, 'Mean Energy', 'blue', 'Mean Energy (Wh)'),
        (max_energy, 'Max Energy', 'green', 'Max Energy (Wh)'),
        (min_energy, 'Min Energy', 'red', 'Min Energy (Wh)'),
        (std_energy, 'Energy Std Dev', 'purple', 'Energy Std Dev (Wh)'),
        (range_energy, 'Energy Range', 'orange', 'Energy Range (Wh)'),
        (median_energy, 'Energy Median', 'brown', 'Energy Median (Wh)'),
        (skew_energy, 'Energy Skewness', 'darkcyan', 'Skewness'),
        (kurtosis_energy, 'Energy Kurtosis', 'darkmagenta', 'Kurtosis'),
    ]

    for i in range(0, len(metrics), 4):
        fig, axs = plt.subplots(2, 2, figsize=(12, 8))
        fig.suptitle('Energy Feature Plots', fontsize=16)
        
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
        'energy_mean': avg_energy,
        'energy_max': max_energy,
        'energy_min': min_energy,
        'energy_std': std_energy,
        'energy_range': range_energy,
        'energy_median': median_energy,
        'energy_skewness': skew_energy,
        'energy_kurtosis': kurtosis_energy
    })
