# charge_voltage_features
import pandas as pd
import numpy as np

def charge_voltage_features(path_sorted, voltage_cutoff=4.2, 
                              f1_start_time=1000, f1_end_time=1500, 
                              f2_voltage_start=2.7, f2_voltage_end=4.2):
    """
    計算每個 cycle 的 F1 和 F2 特徵：
    F1: 1000~1500 秒之間的平均 (charging Voltages - 4.2V)
    F2: 從電壓到達 2.7V 到 4.2V 的充電時間
    """

    results = []
    cycle_counter = 1

    for p in path_sorted:
        try:
            df = pd.read_excel(p, sheet_name=1)

            if not {'Cycle_Index', 'Voltage(V)', 'Current(A)', 'Test_Time(s)'}.issubset(df.columns):
                continue

            file_cycles = sorted(set(df['Cycle_Index'].dropna()))
            for cycle in file_cycles:
                row = {'cycle': cycle_counter}
                df_cycle = df[df['Cycle_Index'] == cycle]

                # ==== F1 ====
                mask_f1 = (
                    (df_cycle['Current(A)'] > 0) &
                    (df_cycle['Test_Time(s)'] >= f1_start_time) &
                    (df_cycle['Test_Time(s)'] <= f1_end_time)
                )
                voltages_f1 = df_cycle[mask_f1]['Voltage(V)'].dropna().values
                if len(voltages_f1) > 0:
                    row['f1_feature'] = np.mean(voltages_f1 - voltage_cutoff)
                else:
                    row['f1_feature'] = np.nan

                # ==== F2 ====
                df_charge = df_cycle[df_cycle['Current(A)'] > 0].copy()
                if not df_charge.empty:
                    reach_end = df_charge[df_charge['Voltage(V)'] >= f2_voltage_end]
                    if not reach_end.empty:
                        t_end = reach_end['Test_Time(s)'].iloc[0]

                        reach_start = df_charge[df_charge['Voltage(V)'] >= f2_voltage_start]
                        if not reach_start.empty:
                            t_start = reach_start['Test_Time(s)'].iloc[0]
                        else:
                            t_start = df_charge['Test_Time(s)'].iloc[0]  # fallback

                        row['f2_feature'] = t_end - t_start
                    else:
                        row['f2_feature'] = np.nan
                else:
                    row['f2_feature'] = np.nan

                results.append(row)
                cycle_counter += 1

        except Exception as e:
            print(f"錯誤讀取檔案 {p}: {e}")

    return pd.DataFrame(results)
