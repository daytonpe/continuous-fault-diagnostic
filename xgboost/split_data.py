import pandas as pd
import numpy as np
"""
# Program to find most frequent
# element in a list
# https://www.geeksforgeeks.org/python-find-most-frequent-element-in-a-list/
"""


def most_frequent(List):
    return max(set(List), key=List.count)


def split_data(DW, X):
    """
    DW - Data Window size to split the data X. I.e. how many metric readings should we flatten into a single array for classification.
    X - array of metric reading arrays

    Take an array of array, for every DW indices, flatten them into a single model input vector. For example

    Input:
    DW = 2
    X = [[A,B],[B,C],[D,E],[F,G]]

    Output: [[A,B,B,C],[D,E,F,G]]

    """
    i = 0
    doc = []
    doc_row = []
    for row in X:
        i = i + 1
        for metric in row:
            doc_row.append(metric)
        if i % DW == 0:
            i = 0
            doc.append(doc_row)
            doc_row = []
    return doc


def split_labels(DW, Y):
    '''
    DW - Data Window size to split the data Y. I.e. how many metric readings labels should we flatten into a single label
    Y - array of metric reading labels

    Take an array of arrays containing one label each and turn them into a label for the data window. Data window label
    calculated by finding most frequent label in the data.
    '''
    arr2d = split_data(DW, Y)
    norm_arr = []
    for arr in arr2d:
        norm_arr.append(most_frequent(arr))
    return norm_arr
