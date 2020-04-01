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
    arr2d = split_data(DW, Y)
    norm_arr = []
    for arr in arr2d:
        norm_arr.append(most_frequent(arr))
    return norm_arr
