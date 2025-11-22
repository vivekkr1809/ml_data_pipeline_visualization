"""Generate sample datasets for latent space visualization testing"""
import numpy as np
import pandas as pd
from sklearn.datasets import make_classification, make_blobs

# Set random seed for reproducibility
np.random.seed(42)

# Dataset 1: Classification dataset with multiple features
print("Generating classification dataset...")
X_class, y_class = make_classification(
    n_samples=300,
    n_features=20,
    n_informative=15,
    n_redundant=3,
    n_repeated=0,
    n_classes=3,
    n_clusters_per_class=2,
    weights=[0.3, 0.4, 0.3],
    flip_y=0.01,
    class_sep=1.0,
    random_state=42
)

# Create DataFrame with feature names
feature_names = [f'feature_{i+1}' for i in range(20)]
df_class = pd.DataFrame(X_class, columns=feature_names)
df_class['target'] = y_class
df_class['target_name'] = df_class['target'].map({0: 'Class_A', 1: 'Class_B', 2: 'Class_C'})

# Save as CSV
df_class.to_csv('sample_classification_data.csv', index=False)
print(f"Saved sample_classification_data.csv: {df_class.shape}")

# Save as Parquet
df_class.to_parquet('sample_classification_data.parquet', index=False, engine='pyarrow')
print(f"Saved sample_classification_data.parquet: {df_class.shape}")

# Dataset 2: Blobs dataset (well-separated clusters)
print("\nGenerating blobs dataset...")
X_blobs, y_blobs = make_blobs(
    n_samples=400,
    n_features=15,
    centers=4,
    cluster_std=2.0,
    random_state=42
)

# Create DataFrame
feature_names_blobs = [f'dimension_{i+1}' for i in range(15)]
df_blobs = pd.DataFrame(X_blobs, columns=feature_names_blobs)
df_blobs['cluster'] = y_blobs
df_blobs['cluster_name'] = df_blobs['cluster'].map({
    0: 'Cluster_1',
    1: 'Cluster_2',
    2: 'Cluster_3',
    3: 'Cluster_4'
})

# Save as CSV
df_blobs.to_csv('sample_blobs_data.csv', index=False)
print(f"Saved sample_blobs_data.csv: {df_blobs.shape}")

# Save as Parquet
df_blobs.to_parquet('sample_blobs_data.parquet', index=False, engine='pyarrow')
print(f"Saved sample_blobs_data.parquet: {df_blobs.shape}")

# Dataset 3: Continuous target (regression-like)
print("\nGenerating continuous target dataset...")
n_samples = 250
n_features = 12

# Generate features
X_cont = np.random.randn(n_samples, n_features)

# Create a continuous target based on a combination of features
y_cont = (
    2.0 * X_cont[:, 0] +
    1.5 * X_cont[:, 1] -
    0.8 * X_cont[:, 2] +
    np.random.randn(n_samples) * 0.5
)

# Create DataFrame
feature_names_cont = [f'var_{i+1}' for i in range(n_features)]
df_cont = pd.DataFrame(X_cont, columns=feature_names_cont)
df_cont['response'] = y_cont

# Save as CSV
df_cont.to_csv('sample_continuous_data.csv', index=False)
print(f"Saved sample_continuous_data.csv: {df_cont.shape}")

# Save as Parquet
df_cont.to_parquet('sample_continuous_data.parquet', index=False, engine='pyarrow')
print(f"Saved sample_continuous_data.parquet: {df_cont.shape}")

print("\n✓ All sample datasets generated successfully!")
print("\nUsage:")
print("1. Load any CSV or Parquet file in the application")
print("2. Select 'PCA Latent Space' or 't-SNE Latent Space' plot type")
print("3. Optionally select a target column for coloring (e.g., 'target', 'cluster', 'response')")
print("4. Adjust parameters and click 'Generate Plot'")
