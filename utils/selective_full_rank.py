import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

# Load your data
data = pd.read_csv("train_constant.csv")

# Separate the 'S' column if it exists
if 'S' in data.columns:
    S_column = data['S']
    data = data.drop(columns=['S'])
else:
    S_column = None

# Step 1: Remove constant and near-constant features
data = data.loc[:, data.apply(lambda x: x.nunique() > 1, axis=0)]

# Step 2: Remove highly correlated features
def remove_highly_correlated(df, threshold=0.95):
    corr_matrix = df.corr().abs()
    upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
    to_drop = [column for column in upper.columns if any(upper[column] > threshold)]
    return df.drop(columns=to_drop)

data = remove_highly_correlated(data)

# Step 3: Check for full rank and iteratively remove columns to ensure full rank
def ensure_full_rank(df):
    cols = df.columns.tolist()
    while np.linalg.matrix_rank(df.values) < len(cols):
        # Find a column with the lowest variance to remove
        variances = df.var()
        col_to_drop = variances.idxmin()
        df = df.drop(columns=[col_to_drop])
        cols.remove(col_to_drop)
    return df

# Apply the function to ensure full rank
data_full_rank = ensure_full_rank(data)

# Reattach the 'S' column if it was removed
if S_column is not None:
    data_full_rank['S'] = S_column.values

# Save the cleaned data
data_full_rank.to_csv("train_full_rank.csv", index=False)
