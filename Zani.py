import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

def extract_time_features(path_sorted):
    cycle_list = []
    ccct_list = []
    cvct_list = []
    discharge_time_list = []
    cycle_counter = 1  # 全域 cycle 累加器

    for path in path_sorted:
        try:
            df = pd.read_excel(path, sheet_name=1)
            if 'Cycle_Index' not in df.columns or 'Step_Time(s)' not in df.columns or 'Current(A)' not in df.columns:
                continue

            file_cycles = sorted(set(df['Cycle_Index'].dropna()))
            for cycle in file_cycles:
                cycle_df = df[df['Cycle_Index'] == cycle].copy()
                cycle_df = cycle_df.sort_values(by='Test_Time(s)')  # 確保時間順序

                # 找到第一次 Voltage >= 4.2 的時間點 (視為 CC → CV 切換點)
                cv_start_idx = cycle_df[(cycle_df['Voltage(V)'] >= 4.2) & (cycle_df['Current(A)'] > 0)].index
                if not cv_start_idx.empty:
                    cv_start_time = cycle_df.loc[cv_start_idx[0], 'Test_Time(s)']
                else:
                    cv_start_time = None

                # CCCT：電壓 < 4.2 且電流 > 0，直到進入 CV 開始
                cc_df = cycle_df[(cycle_df['Current(A)'] > 0) & (cycle_df['Voltage(V)'] < 4.2)]
                if cv_start_time is not None:
                    cc_df = cc_df[cc_df['Test_Time(s)'] < cv_start_time]
                ccct = cc_df['Step_Time(s)'].sum() if not cc_df.empty else 0

                # CVCT：從開始進入 CV 到電流 < 0.05A
                if cv_start_time is not None:
                    after_cv_df = cycle_df[(cycle_df['Test_Time(s)'] >= cv_start_time) & (cycle_df['Current(A)'] > 0)]
                    cv_end_df = after_cv_df[after_cv_df['Current(A)'] < 0.05]
                    if not cv_end_df.empty:
                        cv_end_time = cv_end_df['Test_Time(s)'].iloc[0]
                        cv_phase = after_cv_df[after_cv_df['Test_Time(s)'] <= cv_end_time]
                        cvct = cv_phase['Step_Time(s)'].sum() if not cv_phase.empty else 0
                    else:
                        cvct = 0
                else:
                    cvct = 0

                # Discharge Time
                dis_phase = cycle_df[cycle_df['Current(A)'] < 0]
                discharge_time = dis_phase['Step_Time(s)'].sum() if not dis_phase.empty else 0

                # 儲存特徵
                cycle_list.append(cycle_counter)
                ccct_list.append(ccct)
                cvct_list.append(cvct)
                discharge_time_list.append(discharge_time)
                cycle_counter += 1

        except Exception as e:
            print(f"讀取檔案錯誤 {path}: {e}")

    # 畫圖 (1列3行)
    fig, axs = plt.subplots(1, 3, figsize=(18, 5))
    fig.suptitle('Charge & Discharge Time Features', fontsize=18)

    axs[0].scatter(cycle_list, ccct_list, label='CCCT', color='orange')
    axs[0].set_title('Constant Current Charge Time')
    axs[0].set_xlabel('Cycle')
    axs[0].set_ylabel('Time (s)')
    axs[0].grid(True)

    axs[1].scatter(cycle_list, cvct_list, label='CVCT', color='green')
    axs[1].set_title('Constant Voltage Charge Time')
    axs[1].set_xlabel('Cycle')
    axs[1].set_ylabel('Time (s)')
    axs[1].grid(True)

    axs[2].scatter(cycle_list, discharge_time_list, label='Discharge Time', color='blue')
    axs[2].set_title('Discharge Time')
    axs[2].set_xlabel('Cycle')
    axs[2].set_ylabel('Time (s)')
    axs[2].grid(True)

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.show()

    return pd.DataFrame({
        'cycle': cycle_list,
        'CCCT': ccct_list,
        'CVCT': cvct_list,
        'Discharge_Time': discharge_time_list
    })
