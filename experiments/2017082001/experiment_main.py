import sys
sys.path.append('../../')
from experiments.xgboost_experiment import XGBoostExperiment

if __name__ == "__main__":
    experiment = XGBoostExperiment(
        './data/processed/train_data_svm.txt',
        './data/processed/test_data_svm.txt'
        )
    experiment()