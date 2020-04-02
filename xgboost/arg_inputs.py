import argparse


def get_input_args():
    """
    Retrieves and parses the command line arguments created and defined using
    the argparse module. This function returns these arguments as an
    ArgumentParser object.
     3 command line arguements are created:
       dir - Path to the pet image files(default- 'pet_images/')
       arch - CNN model architecture to use for image classification(default-
              pick any of the following vgg, alexnet, resnet)
       dogfile - Text file that contains all labels associated to dogs(default-
                'dognames.txt'
    Parameters:
     None - simply using argparse module to create & store command line arguments
    Returns:
     parse_args() -data structure that stores the command line arguments object
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
