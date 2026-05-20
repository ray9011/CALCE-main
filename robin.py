# robin.py
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import SpectralClustering

def feature_clustering_pca_spectral(df, n_clusters=4, n_components=5, random_state=42):
    """
    對特徵（欄）進行 PCA 降維後再進行 Spectral Clustering 分群。
    df: 包含多個欄位的 DataFrame，shape = (樣本數, 特徵數)
    return: pd.Series，index 為特徵名稱，value 為其所屬群組
    """
    if df.shape[1] < 3:
        raise ValueError("特徵數過少，無法進行有效的 Spectral Clustering。至少需要 3 個特徵。")

    features = df.T  # shape: (特徵數, 樣本數)
    pca = PCA(n_components=n_components, random_state=random_state)
    pca_features = pca.fit_transform(features)

    clustering = SpectralClustering(
        n_clusters=n_clusters,
        affinity='nearest_neighbors',
        n_neighbors=min(10, features.shape[0] - 1),
        random_state=random_state
    )
    cluster_labels = clustering.fit_predict(pca_features)

    return pd.Series(cluster_labels, index=df.columns)
