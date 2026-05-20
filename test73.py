import pandas as pd
import matplotlib.pyplot as plt

def main():
    # ✅ 直接讀取已處理好的檔案
    df = pd.read_csv(r"C:\Users\1129\Desktop\CALCE-main\contribution_percent.csv", index_col=0)

    # ✅ 依照貢獻度排序
    df = df.sort_values(by='contribution_percent', ascending=False)

    print("\n📋 特徵貢獻百分比（前 10 名）：")
    print(df.head(10))

    # ✅ 繪製長條圖
    plt.figure(figsize=(10, 16))  # 調整長寬以適應橫向排列
    plt.barh(df.index, df['contribution_percent'], color='skyblue')  # 改用 barh
    plt.xlabel("Contribution Percent")  # 原本的 y 軸變成 x 軸
    plt.title("Feature Contribution Percentages (All Features)")
    plt.gca().invert_yaxis()  # ➤ 翻轉 y 軸順序，最大在上
    plt.tight_layout()
    plt.show()

    plt.savefig(r"C:\Users\1129\Desktop\CALCE-main\contribution_percent_barplot_all.png")
    print("✅ 長條圖已儲存為 contribution_percent_barplot_all.png")

    plt.show()

if __name__ == "__main__":
    main()
