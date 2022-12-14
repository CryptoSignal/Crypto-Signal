from app.analyzers.machinelearning.mlutils import ModelUtil
from app.analyzers.machinelearning.preprocessing import Preprocessing
from app.analyzers.machinelearning.classification import Classification
import pandas as pd
import pytest

@pytest.fixture()
def before():
    print ('\nbefore each test')


def assertion(results):
    for i in range(1, 3):
        assert ((results[0][i] > .5) & (results[0][i] <= 1))

def test_classification():
    clf = Classification()
    historical_data = pd.read_csv("eth_data.csv")
    pre = Preprocessing()
    del historical_data["day"]
    x_train, y_train = pre.Cleansing(historical_data, "up_or_down")
    return clf, x_train, y_train

def test_1(before):
    clf, x_train, y_train = test_classification()
    results = clf.naive_bayes(x_train, y_train, x_train)
    print(results)
    assertion(results)
    return

def test_2(before):
    clf, x_train, y_train = test_classification()
    results = clf.knn(x_train, y_train, x_train)
    print(results)
    assertion(results)
    return

def test_3(before):
    clf, x_train, y_train = test_classification()
    results = clf.svc(x_train, y_train, x_train)
    print(results)
    assertion(results)
    return

def test_4(before):
    clf, x_train, y_train = test_classification()
    results = clf.decision_tree(x_train, y_train, x_train)
    print(results)
    assertion(results)
    return

def test_5(before):
    clf, x_train, y_train = test_classification()
    results = clf.random_forest(x_train, y_train, x_train)
    print(results)
    assertion(results)
    return

def test_6(before):
    clf, x_train, y_train = test_classification()
    results = clf.extra_tree(x_train, y_train, x_train)
    print(results)
    assertion(results)
    return

def test_7(before):
    clf, x_train, y_train = test_classification()
    results = clf.adaboost(x_train, y_train, x_train)
    print(results)
    assertion(results)
    return

def test_8(before):
    clf, x_train, y_train = test_classification()
    results = clf.gradientboosting(x_train, y_train, x_train)
    print(results)
    assertion(results)
    return

def test_9(before):
    clf, x_train, y_train = test_classification()
    results = clf.xgboost(x_train, y_train, x_train)
    print(results)
    assertion(results)
    return

def test_10(before):
    clf, x_train, y_train = test_classification()
    results = clf.logistic_regression(x_train, y_train, x_train)
    print(results)
    assertion(results)
    return

def main():
    test_1()
    return







