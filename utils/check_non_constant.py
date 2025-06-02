import pandas as pd
import sys

def remove_low_variance_columns(df, threshold=1e-5):
    variances = df.var()
    non_constant_cols = variances[variances > threshold].index.tolist()
    return df[non_constant_cols]

if __name__ == "__main__":
    input_file = sys.argv[1]
    output_file = sys.argv[2]

    data = pd.read_csv(input_file)
    filtered_data = remove_low_variance_columns(data, threshold=1e-5)

    print("Columns retained with sufficient variance:", filtered_data.columns.tolist())
    print("Removed low-variance columns:", set(data.columns) - set(filtered_data.columns))

    filtered_data.to_csv(output_file, index=False)
    print(f"Filtered data saved to {output_file}")
