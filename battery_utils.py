import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import cm
import glob
from scipy.interpolate import interp1d  # 放在檔案最上面
import pandas as pd
import os

def drop_outlier(array, count, bins):
    index = []
    range_ = np.arange(1, count, bins)
    for i in range_[:-1]:
        array_lim = array[i:i+bins]
        sigma = np.std(array_lim)
        mean = np.mean(array_lim)
        th_max, th_min = mean + sigma*2, mean - sigma*2
        idx = np.where((array_lim < th_max) & (array_lim > th_min))
        idx = idx[0] + i
        index.extend(list(idx))
    return np.array(index)

def load_battery_data(name, dir_path):
    path = [p for p in glob.glob(dir_path + name + '/*.xlsx') if '~$' not in p]
    dates = [pd.read_excel(p, sheet_name=1)['Date_Time'][0] for p in path]
    idx = np.argsort(dates)
    return np.array(path)[idx]

# def process_battery(path_sorted, name):
#     charge_time_list = []
#     charge_voltage_list = []
#     discharge_capacities = []
#     health_indicator = []
#     internal_resistance = []
#     CCCT = []
#     CVCT = []
#     count = 0

#     total_cycles = 0  # 初始化變數，計算總的 Cycle_Index 長度
    
#     for p in path_sorted:  # <- 多個 Excel 檔路徑
#         df = pd.read_excel(p, sheet_name=1)
#         cycles = list(set(df['Cycle_Index']))
        
#         total_cycles += len(cycles)  # 累加每個檔案的 Cycle_Index 長度

#     # 印出總長度
#     print(f"所有檔案的 Cycle_Index 總長度: {total_cycles}")
    
#     for p in path_sorted: # <- 多個 Excel 檔路徑
#         df = pd.read_excel(p, sheet_name=1)
#         cycles = list(set(df['Cycle_Index']))

#         for c in cycles:  # <- 所有 cycle
#             df_lim = df[df['Cycle_Index'] == c]   # 抓出該 cycle 的資料

#             # Charging
#             df_c = df_lim[(df_lim['Step_Index'] == 2) | (df_lim['Step_Index'] == 4)]
#             c_v = df_c['Voltage(V)'].values
#             c_t = df_c['Test_Time(s)'].values
#             c_t = c_t - c_t[0]

#             if len(c_v) > 10:
#                 charge_time_list.append(c_t)
#                 charge_voltage_list.append(c_v)

#             # CC / CV
#             df_cc = df_lim[df_lim['Step_Index'] == 2]
#             df_cv = df_lim[df_lim['Step_Index'] == 4]
#             if not df_cc.empty and not df_cv.empty:
#                 CCCT.append(np.max(df_cc['Test_Time(s)']) - np.min(df_cc['Test_Time(s)']))
#                 CVCT.append(np.max(df_cv['Test_Time(s)']) - np.min(df_cv['Test_Time(s)']))

#             # Discharging
#             df_d = df_lim[df_lim['Step_Index'] == 7]
#             d_v = df_d['Voltage(V)']
#             d_c = df_d['Current(A)']
#             d_t = df_d['Test_Time(s)']
#             d_im = df_d['Internal_Resistance(Ohm)']

#             # 防止資料不足導致 np.diff 空陣列或 d_c 為空
#             if len(d_t) > 1 and len(d_c) > 1:
#                 time_diff = np.diff(d_t.values)
#                 d_c_vals = d_c.values[1:]  # 對齊 time_diff 長度
                
#                 if len(time_diff) == 0 or len(d_c_vals) == 0:
#                     continue  # 跳過這個 cycle

#                 discharge_capacity = time_diff * d_c_vals / 3600

#                 if len(discharge_capacity) == 0:
#                     continue  # 還是空的就跳過

#                 # Cumulative sum 到每個點
#                 discharge_capacity = [np.sum(discharge_capacity[:n]) for n in range(len(discharge_capacity))]
#                 discharge_capacities.append(-1 * discharge_capacity[-1])

#                 #下5行是定義SOH的關鍵
#                 if len(discharge_capacity) > 1:
#                     dec = np.abs(np.array(d_v) - 3.8)[1:]
#                     start = np.array(discharge_capacity)[np.argmin(dec)]
#                     dec = np.abs(np.array(d_v) - 3.4)[1:]
#                     end = np.array(discharge_capacity)[np.argmin(dec)]
#                     health_indicator.append(-1 * (end - start))
#                 else:
#                     health_indicator.append(np.nan)  # 如果無法計算 SoH，補 NaN

#                 internal_resistance.append(np.mean(d_im))
#                 count += 1
def process_battery(path_sorted, battery_name):
    import os
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    from matplotlib import cm

    charge_time_list = []
    charge_voltage_list = []

    # -------------------------------
    # 讀取所有 Excel
    # -------------------------------
    for p in path_sorted:
        df = pd.read_excel(p, sheet_name=1)
        cycles = list(set(df['Cycle_Index']))

        for c in cycles:
            df_lim = df[df['Cycle_Index'] == c]

            # Charging: Step_Index 2 或 4
            df_c = df_lim[(df_lim['Step_Index'] == 2) | (df_lim['Step_Index'] == 4)]
            c_v = df_c['Voltage(V)'].values
            c_t = df_c['Test_Time(s)'].values
            c_t = c_t - c_t[0]

            if len(c_v) > 10:
                charge_time_list.append(c_t)
                charge_voltage_list.append(c_v)

    # -------------------------------
    # 畫充電曲線圖
    # -------------------------------
    num_curves = len(charge_time_list)
    cmap = cm.Blues_r
    norm = plt.Normalize(vmin=0, vmax=num_curves)

    fig, ax = plt.subplots(figsize=(10, 6))
    for i in range(num_curves):
        ax.plot(charge_time_list[i], charge_voltage_list[i], color=cmap(norm(i)), linewidth=1)

    ax.set_xlabel('Time [s]', fontsize=14)
    ax.set_ylabel('Voltage [V]', fontsize=14)
    ax.set_title(f'Charging Curve - {battery_name}', fontsize=16)
    ax.grid(True)

    # 安全加上 colorbar
    try:
        sm = cm.ScalarMappable(cmap=cmap, norm=norm)
        sm.set_array([])
        cbar = fig.colorbar(sm, ax=ax)
        cbar.set_label("Cycle progression", fontsize=12)
        cbar.ax.set_yticklabels(['New', 'Aged'], fontsize=12)
    except ValueError:
        print("Colorbar skipped due to environment issue.")

    plt.tight_layout()
    plt.show()

    # -------------------------------
    # 輸出 CSV
    # -------------------------------
    output_dir = r"C:\Users\王奕傑\Desktop\CALCE-main\data2"
    os.makedirs(output_dir, exist_ok=True)
    save_path = os.path.join(output_dir, f"{battery_name}_charging_data.csv")

    charging_data = []
    for i, (t, v) in enumerate(zip(charge_time_list, charge_voltage_list)):
        df_temp = pd.DataFrame({
            'cycle': [i+1] * len(t),
            'Times(s)': t,
            'Voltage[V]': v
        })
        charging_data.append(df_temp)

    charging_df = pd.concat(charging_data, ignore_index=True)
    charging_df.to_csv(save_path, index=False, encoding='utf-8-sig')
    print(f"充電曲線數據已儲存至 {save_path}")

    return charging_df


    plot_charging_curves(charge_time_list, charge_voltage_list, name)
    # 從這裡開始改    # 儲存充電電壓隨時間變化
    save_path = fr"C:\Users\王奕傑\Desktop\Darklard\charging_voltage\{name}_charging_voltage.csv"

    # 將每個 cycle 的時間與電壓展平成一個 DataFrame
    charging_data = []
    for i, (t, v) in enumerate(zip(charge_time_list, charge_voltage_list)):
        df_temp = pd.DataFrame({
            'cycle': [i+1] * len(t),
            'time(s)': t,
            'voltage(V)': v
        })
        charging_data.append(df_temp)

    charging_df = pd.concat(charging_data, ignore_index=True)
    charging_df.to_csv(save_path, index=False, encoding='utf-8-sig')
    print(f"充電曲線已儲存至 {save_path}")

    min_len = min(len(discharge_capacities), len(health_indicator), len(internal_resistance), len(CCCT), len(CVCT))
    idx = drop_outlier(discharge_capacities[:min_len], count, 40).astype(int)
    print(f"總 cycle 數: {count}")
    print(f"成功取得的放電容量數量: {len(discharge_capacities)}")
    print(f"drop_outlier 保留下來的 idx 長度: {len(idx)}")

    # 繪製出來的是所有 Excel 檔案（也就是所有 cycle）合併後的一條 SoH 曲線，這條線是混合了所有資料的單一趨勢。

    return pd.DataFrame({
        'cycle': np.linspace(1, idx.shape[0], idx.shape[0]),
        'capacity': np.array(discharge_capacities)[:min_len][idx],
        'SoH': np.array(health_indicator)[:min_len][idx],
        'resistance': np.array(internal_resistance)[:min_len][idx],
        'CCCT': np.array(CCCT)[:min_len][idx],
        'CVCT': np.array(CVCT)[:min_len][idx]
    })
    

# def plot_charging_curves(time_list, voltage_list, name):
#     num_curves = len(time_list)
#     colors = cm.Blues_r(np.linspace(0, 1, num_curves))
#     plt.figure(figsize=(10, 6))
#     for i in range(num_curves):
#         plt.plot(time_list[i], voltage_list[i], color=colors[i], linewidth=1)
#     plt.xlabel('Time [s]', fontsize=14)
#     plt.ylabel('Voltage [V]', fontsize=14)
#     plt.title(f'Charging Curve - {name}', fontsize=16)
#     plt.grid(True)
#     sm = plt.cm.ScalarMappable(cmap=cm.Blues_r)
#     sm.set_array([])
#     cbar = plt.colorbar(sm, ticks=[0, 1])
#     cbar.ax.set_yticklabels(['New', 'Aged'], fontsize=12)
#     plt.tight_layout()
#     plt.show()

# def plot_charging_curves(time_list, voltage_list, name):
#     num_curves = len(time_list)
#     cmap = cm.Blues_r
#     norm = plt.Normalize(vmin=0, vmax=num_curves)  # 用曲線數量做顏色範圍

#     plt.figure(figsize=(10, 6))
#     for i in range(num_curves):
#         plt.plot(time_list[i], voltage_list[i], color=cmap(norm(i)), linewidth=1)

#     plt.xlabel('Time [s]', fontsize=14)
#     plt.ylabel('Voltage [V]', fontsize=14)
#     plt.title(f'Charging Curve - {name}', fontsize=16)
#     plt.grid(True)

#     sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
#     sm.set_array([])

#     cbar = plt.colorbar(sm)
#     cbar.set_label("Cycle progression", fontsize=12)
#     cbar.ax.set_yticklabels(['New', 'Aged'], fontsize=12)  # 兩端標籤

#     plt.tight_layout()
#     plt.show()
def plot_charging_curves(time_list, voltage_list, name):
    import matplotlib.pyplot as plt
    from matplotlib import cm

    num_curves = len(time_list)
    cmap = cm.Blues_r
    norm = plt.Normalize(vmin=0, vmax=num_curves)  # 用曲線數量做顏色範圍

    fig, ax = plt.subplots(figsize=(10, 6))

    # 畫每條曲線
    for i in range(num_curves):
        ax.plot(time_list[i], voltage_list[i], color=cmap(norm(i)), linewidth=1)

    ax.set_xlabel('Time [s]', fontsize=14)
    ax.set_ylabel('Voltage [V]', fontsize=14)
    ax.set_title(f'Charging Curve - {name}', fontsize=16)
    ax.grid(True)

    # -------------------------------
    # Colorbar 安全寫法
    # -------------------------------
    try:
        sm = cm.ScalarMappable(cmap=cmap, norm=norm)
        sm.set_array([])  # 必須設定 array，matplotlib 需要
        cbar = fig.colorbar(sm, ax=ax)
        cbar.set_label("Cycle progression", fontsize=12)
        cbar.ax.set_yticklabels(['New', 'Aged'], fontsize=12)  # 兩端標籤
    except ValueError:
        print("Colorbar skipped due to environment issue.")

    plt.tight_layout()
    plt.show()

def plot_results(battery, name):
    # -------------------------------
    # 1️⃣ Cycle vs Capacity
    # -------------------------------
    plt.figure(figsize=(9,6))
    plt.plot(battery['cycle'], battery['capacity'], 'b:', label='Battery_' + name)
    plt.xlabel('Cycle')
    plt.ylabel('Capacity')
    plt.legend()
    plt.grid(True)
    plt.show()

    # -------------------------------
    # 2️⃣ SoH vs Internal Resistance
    # -------------------------------
    # plt.figure(figsize=(9,6))
    # sc = plt.scatter(
    #     battery['cycle'], 
    #     battery['SoH'], 
    #     c=battery['resistance'], 
    #     cmap='magma', 
    #     s=10
    # )
    # cbar = plt.colorbar(sc)  # 對應 scatter 物件
    # cbar.set_label('Internal Resistance (Ohm)', fontsize=14, rotation=-90, labelpad=20)
    # plt.xlabel('Number of Cycles', fontsize=14)
    # plt.ylabel('State of Health', fontsize=14)
    # plt.grid(True)
    # plt.show()

    # 10/13
    fig, ax = plt.subplots(figsize=(9,6))

    # 只選有值的資料
    mask = battery['resistance'].notna()
    sc = ax.scatter(
        battery['cycle'][mask],
        battery['SoH'][mask],
        c=battery['resistance'][mask],
        cmap='magma',
        s=10
    )

    if sc.get_array().size > 0:
        cbar = fig.colorbar(sc, ax=ax)
        cbar.set_label('Internal Resistance (Ohm)', fontsize=14, rotation=-90, labelpad=20)

    ax.set_xlabel('Number of Cycles', fontsize=14)
    ax.set_ylabel('State of Health', fontsize=14)
    ax.grid(True)
    plt.tight_layout()
    plt.show()



    # -------------------------------
    # 3️⃣ Subplots for capacity, resistance, CCCT, CVCT
    # -------------------------------
    plt.figure(figsize=(12,9))
    plot_names = ['capacity', 'resistance', 'CCCT', 'CVCT']

    for i, name_i in enumerate(plot_names):
        plt.subplot(2, 2, i+1)
        if name_i in battery.columns:
            plt.scatter(battery['cycle'], battery[name_i], s=10)
        plt.xlabel('Number of Cycles', fontsize=14)
        plt.ylabel(name_i, fontsize=14)
        plt.grid(True)

    plt.tight_layout()
    plt.show()

# def plot_results(battery, name):
#     plt.plot(battery['cycle'], battery['capacity'], 'b:', label='Battery_' + name)
#     plt.xlabel('Cycle')
#     plt.ylabel('Capacity')
#     plt.legend()
#     plt.grid(True)
#     plt.show()

#     plt.figure(figsize=(9,6))
#     plt.scatter(battery['cycle'], battery['SoH'], c=battery['resistance'], cmap='magma', s=10)
#     cbar = plt.colorbar()
#     cbar.set_label('Internal Resistance (Ohm)', fontsize=14, rotation=-90, labelpad=20)
#     plt.xlabel('Number of Cycles', fontsize=14)
#     plt.ylabel('State of Health', fontsize=14)
#     plt.show()

#     plt.figure(figsize=(12,9))
    
#     names = ['capacity', 'resistance', 'CCCT', 'CVCT']
#     for i in range(4):
#         plt.subplot(2, 2, i+1)
#         plt.scatter(battery['cycle'], battery[names[i]], s=10)
#         plt.xlabel('Number of Cycles', fontsize=14)
#         plt.ylabel(names[i], fontsize=14)
#     plt.tight_layout()
#     plt.show()
# def plot_results(battery, name):
#     plt.figure(figsize=(10, 7))
    
#     # 模擬 MIM 對抗攻擊後的預測線：添加高頻擾動
#     SoH_mim = battery['SoH'] + np.sin(battery['cycle'] / 100 * 2 * np.pi) * 0.02
#     SoH_mim = SoH_mim.clip(0, 1)
    
#     # 畫出原始 SoH 散點
#     sc = plt.scatter(battery['cycle'], battery['SoH'], c=battery['resistance'], cmap='magma', s=10, label='True SoH')
    
#     # 畫出攻擊後的曲線
#     plt.plot(battery['cycle'], SoH_mim, color='deepskyblue', linewidth=2, label='MIM Attack Prediction')

#     cbar = plt.colorbar(sc)
#     cbar.set_label('Internal Resistance (Ohm)', fontsize=14, rotation=-90, labelpad=20)
#     plt.xlabel('Number of Cycles', fontsize=14)
#     plt.ylabel('State of Health', fontsize=14)
#     plt.title(f'SoH under MIM Attack - Battery_{name}', fontsize=16)
#     plt.legend(fontsize=12)
#     plt.grid(True)
#     plt.tight_layout()
#     plt.show()

