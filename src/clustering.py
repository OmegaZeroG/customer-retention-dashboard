from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


def perform_clustering(rfm):

    # Scale the data
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(rfm)

    # Apply KMeans clustering
    kmeans = KMeans(n_clusters=4, random_state=42)

    rfm["Cluster"] = kmeans.fit_predict(scaled_data)

    return rfm