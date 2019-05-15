# -*- coding: utf-8 -*-

"""
@author: zhao zi wa
"""
import numpy as np

import xgboost as xgb

from sklearn.linear_model.logistic import LogisticRegression
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB
from sklearn import tree
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, BaggingClassifier, AdaBoostClassifier
from sklearn.grid_search import GridSearchCV


def lr_classifier(x_train, y_train):
    model = LogisticRegression(random_state=0)
    param_grid = {'C': [0.001, 0.01, 0.05, 0.1, 0.5, 1, 5, 10, 100, 1000], 'penalty': ['l1', 'l2']}
    grid_search = GridSearchCV(model, param_grid, scoring='roc_auc', n_jobs=1, verbose=1)
    grid_search.fit(x_train, y_train)
    best_parameters = grid_search.best_estimator_.get_params()
    print('___LR_best_param:', best_parameters)
    model = LogisticRegression(penalty=best_parameters['penalty'], C=best_parameters['C'])
    model.fit(x_train, y_train)
    return model


def svm_classifier(x_train, y_train):
    model = SVC(kernel='rbf', probability=True, random_state=0)
    param_grid = {'C': [0.001, 0.01, 0.1, 1, 10, 100, 1000], 'gamma': [0.001, 0.0001]}
    grid_search = GridSearchCV(model, param_grid, scoring='roc_auc', n_jobs=1, verbose=1)
    grid_search.fit(x_train, y_train)
    best_parameters = grid_search.best_estimator_.get_params()
    print('___SVM_best_param:', best_parameters)
    model = SVC(kernel='rbf', C=best_parameters['C'], gamma=best_parameters['gamma'], probability=True)
    model.fit(x_train, y_train)
    return model


def nb_classifier(x_train, y_train):
    model = GaussianNB()
    model.fit(x_train, y_train)
    return model


def dt_classifier(x_train, y_train):
    model = tree.DecisionTreeClassifier(random_state=0)
    param_grid = {'criterion': ['entropy', 'gini'], 'max_depth': [3, 4, 5, 6, 7]}
    grid_search = GridSearchCV(model, param_grid, scoring='roc_auc', n_jobs=1, verbose=1)
    grid_search.fit(x_train, y_train)
    best_parameters = grid_search.best_estimator_.get_params()
    print('___DT_best_param:', best_parameters)
    model = tree.DecisionTreeClassifier(criterion=best_parameters['criterion'], max_depth=best_parameters['max_depth'])
    model.fit(x_train, y_train)
    return model


def knn_classifier(x_train, y_train):
    model = KNeighborsClassifier()
    param_grid = {'n_neighbors': [5, 10, 20, 50], 'weights': ['uniform', 'distance']}
    grid_search = GridSearchCV(model, param_grid, scoring='roc_auc', n_jobs=1, verbose=1)
    grid_search.fit(x_train, y_train)
    best_parameters = grid_search.best_estimator_.get_params()
    print('___KNN_best_param:', best_parameters)
    model = KNeighborsClassifier(n_neighbors=best_parameters['n_neighbors'], weights=best_parameters['weights'])
    model.fit(x_train, y_train)
    return model


def rf_classifier(x_train, y_train):
    model = RandomForestClassifier(random_state=0)
    param_grid = {'criterion': ['entropy', 'gini'], 'max_depth': [3, 4, 5, 6, 7], 'n_estimators': [50, 100, 150, 200, 250]}
    grid_search = GridSearchCV(model, param_grid, scoring='roc_auc', n_jobs=1, verbose=1)
    grid_search.fit(x_train, y_train)
    best_parameters = grid_search.best_estimator_.get_params()
    print('___RF_best_param:', best_parameters)
    model = RandomForestClassifier(criterion=best_parameters['criterion'], max_depth=best_parameters['max_depth'],
                                   n_estimators=best_parameters['n_estimators'])
    model.fit(x_train, y_train)
    return model


def gbdt_classifier(x_train, y_train):
    #pipeline = Pipeline([('model', GradientBoostingClassifier())])
    model = GradientBoostingClassifier(random_state=0) #n_estimators=50, learning_rate=0.01
    param_grid = {'max_depth': [2, 3, 4, 5, 6, 7], 'n_estimators': [50, 100, 150, 200, 250],
                  'learning_rate': [0.001, 0.01, 0.1, 0.5]}
    #grid_search = GridSearchCV(pipeline, param_grid, scoring='precision', cv=3)
    grid_search = GridSearchCV(model, param_grid, scoring='precision', n_jobs=1, verbose=1)
    grid_search.fit(x_train, y_train)
    best_parameters = grid_search.best_estimator_.get_params()
    print('___GBDT_best_param:', best_parameters)
    model = GradientBoostingClassifier(learning_rate=best_parameters['learning_rate'], max_depth=best_parameters['max_depth'],
                                       n_estimators=best_parameters['n_estimators'])
    model.fit(x_train, y_train)
    return model


def bagging_lr(x_train, y_train):
    model = BaggingClassifier(LogisticRegression(), random_state=0)
    param_grid = {'n_estimators': [5, 10, 15, 20, 25]}
    grid_search = GridSearchCV(model, param_grid, scoring='roc_auc', n_jobs=1, verbose=1)
    grid_search.fit(x_train, y_train)
    best_parameters = grid_search.best_estimator_.get_params()
    print('___bagging_LR_best_param:', best_parameters)
    model = BaggingClassifier(LogisticRegression(), n_estimators=best_parameters['n_estimators'])
    model.fit(x_train, y_train)
    return model


def xg_boost(x_train, y_train):
    model = xgb.XGBClassifier()
    param_grid = {'nthread': [4], 'objective': ['binary:logistic'],
                  'learning_rate': [0.04, 0.05, 0.03], 'max_depth': [5, 8, 11],
                  'min_child_weight': [11], 'silent': [1],
                  'subsample': [0.8], 'colsample_bytree': [0.7],
                  'n_estimators': [5], 'missing': [-999],
                  'seed': [1337]}
    grid_search = GridSearchCV(model, param_grid, scoring='roc_auc', n_jobs=1, verbose=1)
    grid_search.fit(x_train, y_train)
    best_parameters, score, _ = max(grid_search.grid_scores_, key=lambda x: x[1])
    print('Raw AUC score:', score)
    for param_name in sorted(best_parameters.keys()):
        print("%s: %r" % (param_name, best_parameters[param_name]))
    return grid_search


classifiers = {'LR': lr_classifier, 'SVM': svm_classifier, 'NB': nb_classifier, 'DT': dt_classifier,
               'KNN': knn_classifier, 'RF': rf_classifier, 'GBDT': gbdt_classifier, 'lr_bagging': bagging_lr,
               'XGBOOST': xg_boost}