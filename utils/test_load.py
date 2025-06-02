import pandas as pd
import subprocess

def run_mcf_script(r_script_path, csv_path):
    try:
        # Use stdout and stderr for capturing output
        process = subprocess.Popen(
            ['Rscript', r_script_path, csv_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate()  # Capture output and errors
        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, cmd=' '.join(['Rscript', r_script_path, csv_path]), output=stderr)
    except subprocess.CalledProcessError as e:
        print("Error running R script: {}".format(e.output))
        raise  # Re-raise the exception after printing

def load_mcf_coefficients(output_coeff_path):
    # Read the CSV using pandas
    coefficients = pd.read_csv("output_coeff.csv")
    # Exclude the first two rows (intercept and gamma.X) and extract the first column
    coefficients = coefficients.iloc[2:]
    if len(coefficients) == 0:
        raise ValueError("Coefficient extraction failed: No data found after excluding intercept and gamma.X.")
    

    feature_names = coefficients.iloc[:, 0].values  # First column contains feature names
    coeff_values = coefficients.iloc[:, 1].values  # Second column contains coefficients

    # Remove the "x2_ols" prefix from feature names
    feature_names = ["X{}".format(name.split("X")[-1]) if "X" in name else name for name in feature_names]

    return feature_names, coeff_values

run_mcf_script("../../MCF_code/MCF_train_clicks_script.R", "/Users/shantanusingh/Documents/Heckmen LTR/heckman_rank/evaluation/data/pickles/svm_eta0.5_first/train_clicks_see14_0.5.csv")
print(load_mcf_coefficients(""))