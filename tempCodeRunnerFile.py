import pandas as pd
from lightgbm import LGBMRegressor
from shapash.explainer.smart_explainer import SmartExplainer
from sklearn.model_selection import train_test_split

def main():
    print("🚀 讀取資料中...")
    df = pd.read_csv(r"C:\Users\1129\Desktop\CALCE-main\features_CS2_38.csv")
    print("✅ 資料維度：", df.shape)

    y = df['capacity']
    X = df.drop(['capacity', 'cycle'], axis=1)

    print("📊 特徵欄位：", list(X.columns))

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    print("🧠 訓練 LightGBM 模型...")
    model = LGBMRegressor()
    model.fit(X_train, y_train)

    y_pred = pd.Series(model.predict(X_test), index=X_test.index)

    # 將預測值轉換為百分比，並命名為 SOH (%)
    y_pred = y_pred / y_pred.max() * 100  # 或除以初始容量（如 2.0）
    y_pred.name = 'SOH (%)'

    print("🧠 初始化 Shapash SmartExplainer...")
    xpl = SmartExplainer(model=model)
    xpl.compile(x=X_test, y_pred=y_pred, y_target=y_test)
    xpl.label_dict = {'target': 'SOH (%)'}
    print("✅ compile 成功！")

    shap_contrib = xpl.data['contrib_sorted']
    print("\n🔍 SHAP 特徵名稱：", shap_contrib.columns.tolist())

    # 👉 你的原始特徵名稱順序（49個）
    feature_names = [
        'voltage_mean', 'voltage_max', 'voltage_min', 'voltage_std', 'voltage_range',
        'voltage_median', 'voltage_skewness', 'voltage_kurtosis',
        'current_mean', 'current_max', 'current_min', 'current_std', 'current_range',
        'current_median', 'current_skewness', 'current_kurtosis',
        'energy_mean', 'energy_max', 'energy_min', 'energy_std', 'energy_range',
        'energy_median', 'energy_skewness', 'energy_kurtosis',
        'dvdt_mean', 'dvdt_max', 'dvdt_min', 'dvdt_std', 'dvdt_range',
        'dvdt_median', 'dvdt_skewness', 'dvdt_kurtosis',
        'CCCT', 'CVCT', 'Discharge_Time',
        'resistance_mean', 'resistance_max', 'resistance_min', 'resistance_std',
        'resistance_range', 'resistance_median',
        'didt_mean', 'didt_max', 'didt_min', 'didt_std', 'didt_range',
        'didt_median', 'didt_skewness', 'didt_kurtosis'
    ]

    # 平均絕對貢獻值（預設欄位名 contributions_0~）
    mean_abs_contrib = shap_contrib.abs().mean()

    # 檢查長度一致
    assert len(feature_names) == len(mean_abs_contrib), "❌ 特徵數量不一致，請檢查"

    # 替換 index 為原始特徵名稱
    mean_abs_contrib.index = feature_names

    # 儲存 mean_abs_contribution.csv（index 就是正確特徵名）
    mean_abs_contrib.sort_values(ascending=False).to_csv(
        r"C:\Users\1129\Desktop\CALCE-main\mean_abs_contribution.csv"
    )

    # 製作百分比表
    total = mean_abs_contrib.sum()
    contrib_df = pd.DataFrame({
        'mean_abs_contribution': mean_abs_contrib,
        'contribution_percent': mean_abs_contrib / total
    }).sort_values(by='contribution_percent', ascending=False)

    contrib_df.to_csv(r"C:\Users\1129\Desktop\CALCE-main\contribution_percent.csv")
    print("✅ 已儲存 contribution_percent.csv（特徵名稱正確）")

    # 每筆資料 SHAP 加總
    shap_contrib.sum(axis=1).to_csv(
        r"C:\Users\1129\Desktop\CALCE-main\shap_sum_per_sample.csv", header=["shap_sum"]
    )

    print("✅ 每筆 SHAP 總和已儲存 shap_sum_per_sample.csv")
    print("🚀 啟動 Shapash WebApp...")
    xpl.run_app()

if __name__ == "__main__":
    main()
