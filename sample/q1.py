import numpy as np 
import math, random, torch
from copy import deepcopy
from sklearn.metrics import mean_squared_error
import torch.nn as nn
import torch.nn.functional as func
from torch import optim
import torch.nn.functional as F

def load_data(data_file, skip_line = 0):
    f = open(data_file, 'r')
    num = 0
    ret = []
    for line in f.readlines():
        if num < skip_line:
            num += 1
            continue
        line = line.strip('\n').split(',')
        line = [float(i) for i in line]
        ret.append(line)
    return np.array(ret)

def split_data(data, ratio):
    random.shuffle(data)
    num = int(len(data) * ratio)
    train, test = data[: num], data[num: ]
    return train, test

def split_label(data):
    feature, label = [], []
    for d in data:
        feature.append(d[: -1])
        label.append([d[-1]])
    return np.array(feature), np.array(label)

def normalize(data, X_train):
    ret = deepcopy(data)
    r, c = np.shape(data)
    aver, var = X_train.mean(axis = 0), X_train.var(axis = 0)
    for i in range(c):
        ret[:, i] -= aver[i]
        ret[:, i] /= var[i] ** 0.5
    return ret


class Model(nn.Module):
    def __init__(self):
        super().__init__()
        self.f1 = nn.Linear(13, 16)
        self.f2 = nn.Linear(16, 32)
        self.f3 = nn.Linear(32, 1)

    def forward(self, x):
        x = func.relu(self.f1(x))
        x = torch.tanh(self.f2(x))
        x = self.f3(x)
        return x

    def fit(self, data, label, epoch = 20):
        loss_function = nn.L1Loss()
        optimizer = optim.SGD(self.parameters(), lr=0.01, weight_decay= 1e-6, momentum = 0.9, nesterov = True)
        for i in range(epoch):
            self.train()
            n = len(data)
            for j in range(n):
                optimizer.zero_grad()
                Y = self(data)
                loss = loss_function(Y, label)
                loss.backward()
                optimizer.step()

def main():
    data = load_data('boston_house_prices.csv', 2)
    train_data, test_data = split_data(data, 0.7)
        
    X_train, Y_train = split_label(train_data)
    X_test,  Y_test  = split_label(test_data)

    X_test = normalize(X_test, X_train)
    X_train = normalize(X_train, X_train)

    X_train = torch.from_numpy(X_train).float()
    Y_train = torch.from_numpy(Y_train).float()

    model = Model()
    model.fit(X_train, Y_train)

    X_test = torch.from_numpy(X_test).float()

    Y_pred = model(X_test)
    Y_pred = Y_pred.data.numpy()

    print(mean_squared_error(Y_pred, Y_test))

if __name__ == '__main__':
    main()
