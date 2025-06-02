import pandas as pd
import numpy as np
import sys

def is_full_rank(df):
    matrix = df.to_numpy()
    rank = np.linalg.matrix_rank(matrix)
    full_rank = rank == matrix.shape[1]
    return full_rank, rank, matrix.shape[1]

if __name__ == "__main__":
    input_file = "train_full_rank.csv"

    data = pd.read_csv(input_file)
    full_rank, rank, total_columns = is_full_rank(data)
    print(f"Matrix rank: {rank}, Total columns: {total_columns}")

    if full_rank:
        print("The matrix has full rank.")
    else:
        print("The matrix does NOT have full rank; consider dimensionality reduction.")
