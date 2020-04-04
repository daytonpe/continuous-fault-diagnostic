import argparse


def get_input_args():
    """
    Retrieves and parses the command line arguments created and defined using
    the argparse module.
    """

    parser = argparse.ArgumentParser()
    parser.add_argument("--dw", type=int, default=20,
                        help="data window size in number of measurements")
    parser.add_argument("--include-offline-data", type=bool, default=True,
                        help="if false we will only train based on online data rather than a concatenation of the original offline data and the offline data")
    parser.add_argument("--offline-data", type=str, default="data/online-train-XXL.csv",
                        help="csv of data pulled from offline db for offline training")
    parser.add_argument("--mins", type=int, default=15,
                        help="rolling minutes for calculating accuracy")
    parser.add_argument("--model", type=str, default="xgboost/model/pima.pickle.dat",
                        help="model to be used for retraining")
    return parser.parse_args()
