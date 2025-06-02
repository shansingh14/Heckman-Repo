import pandas as pd
from sklearn.decomposition import PCA
import sys

def reduce_dimensionality(df, variance_threshold=0.80):  # Adjusted to 0.80
    pca = PCA()
    pca.fit(df)
    cumulative_variance = pca.explained_variance_ratio_.cumsum()
    n_components = (cumulative_variance >= variance_threshold).argmax() + 1
    reduced_matrix = pca.transform(df)[:, :n_components]
    print(f"Reduced to {n_components} dimensions, explaining {cumulative_variance[n_components-1]:.2%} of variance.")
    return pd.DataFrame(reduced_matrix)

if __name__ == "__main__":
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    data = pd.read_csv(input_file)
    reduced_data = reduce_dimensionality(data, variance_threshold=0.80)

    reduced_data.to_csv(output_file, index=False)
    print(f"Reduced dataset saved as {output_file}")
