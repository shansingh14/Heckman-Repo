import os
import pdb
import argparse
import warnings
import subprocess
import pandas as pd

warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.filterwarnings(action="ignore", module="scipy", message="^internal gelsd")

def warn(*args, **kwargs):
    pass
warnings.warn = warn

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import LogisticRegression
from scipy.stats import norm
# import statsmodels.api as sm



pd.options.mode.chained_assignment = None

def probit(Y, X):   
    clf = LogisticRegression(solver='lbfgs').fit(X, Y)
    return clf.coef_/1.6

def inverse_mills(val):
    return norm.pdf(val) / norm.cdf(val)


def read_data(data_file, file_format='csv'):
    if file_format == 'csv':
        return pd.read_csv(data_file)
    
    if file_format == 'pkl':
        return pd.read_pickle(data_file)
    
    return None


def heckman(train):
    X = train[train.columns.drop(['qid', 'C', 'S', 'R', 'T', 'SC'])]
    Y = train['S']

    gamma = probit(Y, X).T
    lambda_ = inverse_mills(np.matmul(X, gamma))
    
    Y = train['C']
    params = probit(Y, np.append(X, lambda_.reshape(-1,1), 1))
    lam_coeff= params[0][-1]
    x_coeff= params[0][0:-1]
    
    return x_coeff


def eval(df, params,score_name='h_score'):
    # X_test = df[df.columns.drop(['qid', 'C', 'S'])]
    X_test = df[df.columns.drop(['qid', 'C', 'S', 'R', 'T', 'SC'])]
    Eval = df[['qid', 'C']]

    Eval[score_name] = norm.cdf(np.matmul(X_test, params))
    
    return Eval

def eval_out(df, params, score_name, out_file):
    eval_data = eval(df, params,score_name='h_score')
    eval_data['h_score'] = (eval_data['h_score'] - eval_data['h_score'].min()) / (eval_data['h_score'].max() - eval_data['h_score'].min())
    eval_data.to_csv(out_file, index=False)


# Code to utilize MCF instead of Heckman
def run_mcf_script(r_script_path, csv_path):
    try:
        # Use stdout and stderr for capturing output
        process = subprocess.Popen(
            ['Rscript', r_script_path, csv_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate()  # silencing stdout
        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, cmd=' '.join(['Rscript', r_script_path, csv_path]), output=stderr)
    except subprocess.CalledProcessError as e:
        print("Error running R script: {}".format(e.output))
        raise


def load_mcf_coefficients(output_coeff_path):
    coefficients = pd.read_csv("output_coeff.csv")
    # Exclude the first two rows (intercept and gamma.X) and extract the first column
    coefficients = coefficients.iloc[2:]
    if len(coefficients) == 0:
        raise ValueError("Coefficient extraction failed: No data found after excluding intercept and gamma.X.")
    

    feature_names = coefficients.iloc[:, 0].values 
    coeff_values = coefficients.iloc[:, 1].values  

    # remove the "x2_ols" prefix
    feature_names = ["X{}".format(name.split("X")[-1]) if "X" in name else name for name in feature_names]

    return feature_names, coeff_values

def get_mcf_coeff(r_script_path, input_data, output_coeff_path):
    run_mcf_script(r_script_path, input_data)
    return load_mcf_coefficients(output_coeff_path)

def eval_mcf(df, params, features,score_name='h_score'):
    X_test = df[features].values  # Ensure only relevant columns are selected in the correct order

    # Create a new dataframe for evaluation
    Eval = df[['qid', 'C']].copy()  # Copy 'qid' and 'C' columns for output consistency

    # Calculate the score using the provided params
    Eval[score_name] = norm.cdf(np.matmul(X_test, params))

    return Eval

def eval_out_mcf(df, params, features, score_name, out_file):
    eval_data = eval_mcf(df, params, features,score_name='h_score')
    eval_data['h_score'] = (eval_data['h_score'] - eval_data['h_score'].min()) / (eval_data['h_score'].max() - eval_data['h_score'].min())
    eval_data.to_csv(out_file, index=False)


# Methods for Chernozhukov
def get_cherno_coeff(r_script_path, input_data, output_coeff_path):
    """
    Runs the Chernozhukov method and extracts the coefficients.
    """
    run_cherno_script(r_script_path, input_data)
    return load_cherno_coefficients(output_coeff_path)


def run_cherno_script(r_script_path, csv_path):
    """
    Runs the Chernozhukov R script with the input dataset.
    """
    try:
        process = subprocess.Popen(
            ['Rscript', r_script_path, csv_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, cmd=' '.join(['Rscript', r_script_path, csv_path]), output=stderr)
    except subprocess.CalledProcessError as e:
        print("Error running Chernozhukov R script: {}".format(e.output))
        raise

def load_cherno_coefficients(output_coeff_path):
    """
    Reads the Chernozhukov output file and extracts feature coefficients.
    """
    coefficients = pd.read_excel(output_coeff_path)
    feature_names = coefficients.columns[0]  # First column contains feature names

    # Extracting the two coefficient columns
    coeff_0 = coefficients.iloc[:, 0].values
    coeff_1 = coefficients.iloc[:, 1].values

    # Just using y=1 values
    coeff_values = coeff_0

    return feature_names, coeff_values



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-ds', default='data/pickles/pop_eta0_first/', help='pickle data source.')
    parser.add_argument('-fmt', default='csv', help='data file format.')
    parser.add_argument('-see', type=int, default='0', help='see threshold.')
    parser.add_argument('-eta', type=str, default='0', help='eta.')
    parser.add_argument('-o', default='data/result/', help='output directory path')
    args = parser.parse_args()

    # Load train file into dataframe
    train_file = os.path.join(args.ds, 'train_clicks_see%d_%s.%s' % (args.see, args.eta, args.fmt))
    train = read_data(train_file, args.fmt)
    
    train['S'] = train['S'].astype(int)
    train['C'] = train['C'].astype(int)

    # Load test file into dataframe
    test_file = os.path.join(args.ds, 'test_clicks_see%d_%s.%s' % (args.see, args.eta, args.fmt))
    test = read_data(test_file, args.fmt)
    test['C'] = test['C'].astype(int)

    # Learn params through Heckman method
    params = heckman(train) # Heckman
    #features, params = get_mcf_coeff("../../MCF_Code/MCF_train_clicks_script.R", train_file, "r_script_data/output_coeff.csv") # MCF

    # Evaluate train data 
    out_train_file = os.path.join(args.o, 'train_scores_see%d_%s.csv' % (args.see, args.eta))
    eval_out(train, params, score_name='h_score', out_file=out_train_file) # Heckman
    #eval_out_mcf(train, params, features, score_name='h_score', out_file=out_train_file) # MCF
    
    # Evaluate test data 
    out_test_file = os.path.join(args.o, 'test_scores_see%d_%s.csv' % (args.see, args.eta))
    eval_out(test, params, score_name='h_score', out_file=out_test_file) # Heckman
    #eval_out_mcf(test, params, features, score_name='h_score', out_file=out_test_file) # MCF

    




if __name__ == "__main__":
    main()