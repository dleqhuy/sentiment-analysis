import plotly.graph_objects as go
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import unicodedata
import numpy as np
import pickle
import time
import re
import os

from sklearn.model_selection import train_test_split, cross_validate, GridSearchCV
from sklearn.metrics import classification_report, confusion_matrix, plot_roc_curve
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics import roc_auc_score, accuracy_score

from typing import List

class SentimentModel:
    def __init__(self, pmodel, pvector, py):
        self.model = pmodel
        self.vectorizer = pvector[1][0]
        self.model.fit(pvector[1][1], py)
        
    def predict(self, pnew_data):
        new_data = self.vectorizer.transform(pnew_data)
        yhat_class = self.model.predict(new_data)
        yhat_proba = self.model.predict_proba(new_data)
        
        return pd.DataFrame({
            'input': pnew_data,
            'output_proba': [tuple(x) for x in yhat_proba],
            'output_class': yhat_class, 
        })
        
    def info(self):
        print(self.model)
        


def loadData(ppath: str):
    X = pd.read_csv(f"{ppath}/X.csv")
    y = pd.read_csv(f"{ppath}/y.csv")
    
    return X, y



def convertToNFX(series, type: str):
    return series.apply(lambda x: unicodedata.normalize(type, x))
    


def vectorizer(pdata: pd.Series, pmethod: str ,pmin_df=1):
    pdata = convertToNFX(pdata, 'NFC')
    if pmethod == 'bow': vec = CountVectorizer(min_df=pmin_df)
    else: vec = TfidfVectorizer(min_df=pmin_df)
    
    transform = vec.fit_transform(pdata)
    return [vec, transform]


def dataSplitSaved(pdata: pd.DataFrame, ptest_size: float, ppath: str):
    X_train, X_test, y_train, y_test = train_test_split(pdata.normalize_comment,pdata.label, test_size=ptest_size, random_state=42)
    
    path = f"{ppath}/train"
    if not(os.path.exists(path)):
      os.makedirs(path)

    X_train.to_csv(path+"/X.csv", index=False)
    y_train.to_csv(path+"/y.csv", index=False)

    path = f"{ppath}/test"
    if not(os.path.exists(path)):
      os.makedirs(path)

    X_test.to_csv(path+"/X.csv", index=False)
    y_test.to_csv(path+"/y.csv", index=False)
    
    print(f"📢 Your dataset has saved at {ppath}.")
    
def train(lst_models, X_vectorizer, y, cv):
    res_table = []
    for vec_name, vec in X_vectorizer:
        print(f"{vec_name}:")
        X = vec[1]
        for mdl_name, model in lst_models:
            tic = time.time()
            cv_res = cross_validate(model, X, y, cv=cv, return_train_score=True, scoring=['accuracy', 'roc_auc'])
            res_table.append([vec_name, mdl_name,
                              cv_res['train_accuracy'].mean(),
                              cv_res['test_accuracy'].mean(),
                              np.abs(cv_res['train_accuracy'].mean() - cv_res['test_accuracy'].mean()),
                              cv_res['train_accuracy'].std(),
                              cv_res['test_accuracy'].std(),
                              cv_res['fit_time'].mean()
            ])
            toc = time.time()
            print('\tModel {} has been trained in {:,.2f} seconds'.format(mdl_name, (toc - tic)))
            
    
    res_table = pd.DataFrame(res_table, columns=['vectorizer', 'model', 'train_acc', 'test_acc',
                                                 'train_acc_std', 'test_acc_std', 'fit_time'])
    res_table.sort_values(by=['test_acc'], ascending=False, inplace=True)
    return res_table.reset_index(drop=True)     
    
    
def evaluation(tunning_models, X_train_vec, y_train, X_test_vec, y_test):
    res = []
    for name, model in tunning_models:
        model.fit(X_train_vec, y_train)
        y_train_pred = model.predict(X_train_vec)
        y_test_pred = model.predict(X_test_vec)
        train_acc = accuracy_score(y_train, y_train_pred)
        test_acc = accuracy_score(y_test, y_test_pred)
        train_roc_auc = roc_auc_score(y_train, y_train_pred)
        test_roc_auc = roc_auc_score(y_test, y_test_pred)
        res.append([name, train_acc, test_acc, train_roc_auc, test_roc_auc])
        
    res = pd.DataFrame(res, columns=['model', 'train_acc', 'test_acc'])
    res.sort_values(by=['test_acc'], ascending=False, inplace=True)
    
    return res.reset_index(drop=True)
    
    
    
def confusionMatrix(y_true, y_pred):
    target_names = ['Negative', 'Positive']
    print(classification_report(y_true, y_pred, target_names=target_names))
    cm = pd.DataFrame(confusion_matrix(y_true, y_pred), index=target_names, columns=target_names)
    plt.figure(figsize=(6,4))
    sns.heatmap(cm, annot=True, fmt='g')
    plt.title('Confusion matrix')
    plt.xlabel('Predicted values')
    plt.ylabel('Actual values')
    plt.show()

    
def saveByPickle(object, path):
    pickle.dump(object, open(path, "wb"))
    print(f"{object} has been saved at {path}.")



def combinePrediction(a, b, c):
    neg = (a[0] + b[0] + c[0])/3
    pos = (a[1] + b[1] + c[1])/3
    
    return 0 if neg > pos else 1    

def loadByPickle(path):
    with open(path, 'rb') as f:
        return pickle.load(f)