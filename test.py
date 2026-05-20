import pandas as pd
import glob
import os

txt_files = glob.glob(r'C:/Users/1129/Desktop/CALCE-main/dataset/CS2_8/*.txt')

save_dir = r'C:/Users/1129/Desktop/CALCE-main/dataset/CS2_8_xlsx'
os.makedirs(save_dir, exist_ok=True)

for file in txt_files:
    df = pd.read_csv(file, sep='\t', engine='python')  # tab 分隔
    filename = os.path.splitext(os.path.basename(file))[0]
    df.to_excel(f'{save_dir}/{filename}.xlsx', index=False)
