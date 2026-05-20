import numpy as np
import os
import pandas as pd
import matplotlib.pyplot as plt


# 切換虛擬機指令 cd C:\Users\王奕傑\Desktop\CALCE-main
# venv37\Scripts\activate
# %% 容量特徵提取

# %%電壓特徵擷取
def extract_voltage_features(file_path):
    print(f"正在處理檔案（電壓）: {file_path}")
    try:
        df = pd.read_excel(file_path, sheet_name="Channel_1-006")
    except Exception as e:
        print(f" 無法讀取 {file_path}: {e}")
        return None

    if 'Cycle_Index' not in df.columns or 'Voltage(V)' not in df.columns:
        print(f" 檔案 {file_path} 缺少必要欄位")
        return None

    grouped = df.groupby('Cycle_Index')['Voltage(V)']
    features = pd.DataFrame({
        'Voltage_Mean': grouped.mean(),
        'Voltage_Std': grouped.std(),
        'Voltage_Max': grouped.max(),
        'Voltage_Min': grouped.min(),
        'Voltage_Range': grouped.max() - grouped.min(),
        'Voltage_Q25': grouped.quantile(0.25),
        'Voltage_Q50': grouped.quantile(0.50),
        'Voltage_Q75': grouped.quantile(0.75),
    })

    print(f"✅ 電壓特徵提取成功: {features.head()}")
    return features

def generate_voltage_plots(features_dict): 
    feature_names = ['Voltage_Mean', 'Voltage_Std', 'Voltage_Max', 'Voltage_Min', 
                     'Voltage_Range', 'Voltage_Q25', 'Voltage_Q50', 'Voltage_Q75']
    
    for feature in feature_names:
        plt.figure(figsize=(10, 6))
        for filename, features in features_dict.items():
            if feature in features.columns:
                plt.plot(features.index, features[feature], label=filename.replace(".xlsx", ""))
        plt.xlabel("Cycle Index")
        plt.ylabel(feature)
        plt.title(f"{feature} across all files")
        plt.legend(title="Files", bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid(True)
        plt.tight_layout()
        plt.show()

def process_voltage_features_in_directory(directory_path):
    features_dict = {}
    print(f"開始處理電壓特徵，目錄: {directory_path}")
    for filename in os.listdir(directory_path):
        if filename.endswith(".xlsx") and not filename.startswith("~$"):
            file_path = os.path.join(directory_path, filename)
            features = extract_voltage_features(file_path)
            if features is not None:
                features_dict[filename] = features

    if features_dict:
        print(" 所有電壓特徵完成，開始繪圖...")
        generate_voltage_plots(features_dict)
    else:
        print(" 沒有有效的電壓資料！")

# %% 電流特徵擷取
def extract_current_features(file_path):
    print(f"正在處理檔案（電流）: {file_path}")
    try:
        df = pd.read_excel(file_path, sheet_name="Channel_1-006")
    except Exception as e:
        print(f" 無法讀取 {file_path}: {e}")
        return None

    if 'Cycle_Index' not in df.columns or 'Current(A)' not in df.columns:
        print(f" 檔案 {file_path} 缺少必要欄位")
        return None

    grouped = df.groupby('Cycle_Index')['Current(A)']
    features = pd.DataFrame({
        'Current_Mean': grouped.mean(),
        'Current_Std': grouped.std(),
        'Current_Max': grouped.max(),
        'Current_Min': grouped.min(),
        'Current_Range': grouped.max() - grouped.min(),
        'Current_Q25': grouped.quantile(0.25),
        'Current_Q50': grouped.quantile(0.50),
        'Current_Q75': grouped.quantile(0.75),
    })

    print(f"✅ 電流特徵提取成功: {features.head()}")
    return features

def generate_current_plots(features_dict): 
    feature_names = ['Current_Mean', 'Current_Std', 'Current_Max', 'Current_Min', 
                     'Current_Range', 'Current_Q25', 'Current_Q50', 'Current_Q75']
    
    for feature in feature_names:
        plt.figure(figsize=(10, 6))
        for filename, features in features_dict.items():
            if feature in features.columns:
                plt.plot(features.index, features[feature], label=filename.replace(".xlsx", ""))
        plt.xlabel("Cycle Index")
        plt.ylabel(feature)
        plt.title(f"{feature} across all files")
        plt.legend(title="Files", bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid(True)
        plt.tight_layout()
        plt.show()

def process_current_features_in_directory(directory_path):
    features_dict = {}
    print(f"開始處理電流特徵，目錄: {directory_path}")
    for filename in os.listdir(directory_path):
        if filename.endswith(".xlsx") and not filename.startswith("~$"):
            file_path = os.path.join(directory_path, filename)
            features = extract_current_features(file_path)
            if features is not None:
                features_dict[filename] = features

    if features_dict:
        print(" 所有電流特徵完成，開始繪圖...")
        generate_current_plots(features_dict)
    else:
        print(" 沒有有效的電流資料！")

# %% 內阻特徵提取

