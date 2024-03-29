# -*- coding: utf-8 -*-
"""HR Analytics Attrition Analysis.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1tw1A19Igx7wm0Z1CC71qKb70v5w63QMV
"""

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import make_column_selector, make_column_transformer
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV
from sklearn.impute import SimpleImputer
from sklearn.tree import plot_tree
from sklearn import set_config
set_config(display='diagram')

#import accuracy, precision, recall, classification report, and confusion matrix scoring functions
from sklearn.metrics import accuracy_score, precision_score, recall_score, classification_report, confusion_matrix

#Importing the KNN Classifier and RandomForest Classifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier

path1 = '/content/drive/MyDrive/CD: Project 2: Attrition Analysis/data_dictionary.xlsx'
path2 = '/content/drive/MyDrive/CD: Project 2: Attrition Analysis/employee_survey_data.csv'
path3 = '/content/drive/MyDrive/CD: Project 2: Attrition Analysis/general_data.csv'
path4 = '/content/drive/MyDrive/CD: Project 2: Attrition Analysis/in_time.csv'
path5 = '/content/drive/MyDrive/CD: Project 2: Attrition Analysis/out_time.csv'
path6 = '/content/drive/MyDrive/CD: Project 2: Attrition Analysis/manager_survey_data.csv'

#data1 = pd.read_csv(path1)
es_data = pd.read_csv(path2)
gen_data = pd.read_csv(path3)
in_time_data = pd.read_csv(path4)
out_time_data = pd.read_csv(path5)
manager_data = pd.read_csv(path6)

es_data.head()

gen_data.head()

in_time_data.head()

out_time_data.head()

manager_data.head()

in_time_data.fillna(0, inplace=True)
out_time_data.fillna(0, inplace=True)

in_time_data.iloc[:, 1:] = in_time_data.iloc[:, 1:].apply(pd.to_datetime, errors='coerce')

out_time_data.iloc[:, 1:] = out_time_data.iloc[:, 1:].apply(pd.to_datetime, errors='coerce')

total_time = in_time_data.append(out_time_data)

total_time=total_time.diff(periods=4410)
total_time=total_time.iloc[4410:]

total_time.reset_index(inplace=True)
total_time.head()

total_time.drop(columns=['index', 'Unnamed: 0'], axis=1, inplace=True)
total_time.head()

total_time.drop(['2015-01-01', '2015-01-26','2015-03-05','2015-05-01','2015-07-17','2015-09-17','2015-10-02','2015-11-09','2015-11-10','2015-11-11','2015-12-25'], axis = 1,inplace=True)

total_time['mean_time']=total_time.mean(axis=1)

total_time.mean_time = total_time.mean_time.apply(lambda x : int(str(x).split(' ')[2].split(':')[0]) + int((str(x).split(' ')[2].split(':')[1]))/60
                           + float((str(x).split(' ')[2].split(':')[2]))/3600)

total_time.reset_index(inplace=True)

total_time = total_time.rename(columns={'index':'EmployeeID'})
total_time.head()

total_time = total_time.drop((total_time.columns[1:-1]), axis = 1)

total_time.head()

gen_data = gen_data.merge(manager_data, on ='EmployeeID')

data = gen_data.merge(es_data)

data = pd.merge(data, total_time, on='EmployeeID')
data.head()

data.drop(['EmployeeCount', 'StandardHours', 'Over18'], axis = 1, inplace = True)

"""### Inconsistency in the dataset:
After investigation, I did not see any inconsistency in the dataset.

### There are missing values in:
EnvironmentSatisfaction (float),
JobSatisfaction (float),
WorkLifeBalance (float),
NumCompaniesWorked (float)

Because this is an employee attritino data we will empute the missing values using MEAN (average) for environment satisfaction, job satisfaction, work life balance, and number of companies worked for.

###Ordinal Encode:
After investigation - It seems that the only column that would need to be ordinal encoded is the target "Attrition". Given that this alot of the dataset is generated from a survey the columns are organized as ordinal features with distinct ordering (Environment Satisfaction, Job Satisfaction, Work life Balance, StockOptionLevel, Job Level, and Education.
"""

def make_plot(feature_name, x_ticks = 'not_needed'):
    """This function is used to generate a countplot for the passed input feature present
    in df_eda dataframe. Appropriate plot title, xlabel, ylabel, lengend are also added.
    The last part of this function also places a percentage value over each bar of
    generated countplot.

    Args:
        feature_name: the feature name in string format.
        x_ticks: default value is 'not_needed'. If you want to customize xticks then pass
                 a list containing new xticks.

    """
    # Initialize a figure
    plt.figure(figsize = (18,7))

    # Generate a countplot for the passed feature_name
    ax = sns.countplot(x=feature_name, hue='Attrition', data=data, palette='Paired')

    # Check if custom x_tick is needed or not
    if x_ticks != 'not_needed':
        # Generate index of xticks
        ticks_index = [i for i in range(len(x_ticks))]

        # set new xticks by passing ticks_index and custom xtick labels
        ax.set(xticks=ticks_index, xticklabels=x_ticks)

        plt.xlabel(feature_name,fontsize  = 14)
    plt.ylabel('Employee Count',fontsize  = 14)
    plt.title('{} vs Attrition'.format(feature_name), fontsize = 18)
    plt.legend(fontsize = 14)

    # From axis.patches get bar lengths
    get_bars = ax.patches
    half_bar_length = int(len(get_bars)/2)
    bar_left = get_bars[:half_bar_length]
    bar_right = get_bars[half_bar_length:]

    # Place %employees on top of each bar
    for L, R in zip(bar_left, bar_right):
        left_height = L.get_height()
        right_height = R.get_height()
        length_total = left_height + right_height

        # place calculated employee percentage on top of each bar
        ax.text(L.get_x() + L.get_width()/2., left_height + 30, '{0:.0%}'.format(left_height/length_total), ha="center")
        ax.text(R.get_x() + R.get_width()/2., right_height + 30, '{0:.0%}'.format(right_height/length_total), ha="center")

make_plot('Age')

make_plot('WorkLifeBalance')

attrition_rep = {'Yes':1, 'No':0}
data['Attrition'].replace(attrition_rep, inplace=True)
data['Attrition'].value_counts()

gender_rep = {'Yes':1, 'No':0}
data['Gender'].replace(gender_rep, inplace=True)
data['Gender'].value_counts()

X = data.drop(columns='Attrition')
y = data['Attrition']

X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42)

# Pre-Process for ML with a pipeline
cat_select = make_column_selector(dtype_include='object')
num_select = make_column_selector(dtype_include='number')

mean_imputer = SimpleImputer(strategy='mean',) # this is impute the missing values
freg_imputer = SimpleImputer(strategy='most_frequent')

scaler = StandardScaler()
ohe = OneHotEncoder(sparse=False, handle_unknown='ignore')

# Setup the pipelines for the numeric and categorical data
num_processor = make_pipeline(mean_imputer, scaler)
cat_processor = make_pipeline(freg_imputer, ohe)

# Setup the tuples to pair the processors with the make column selectors
num_tuple = (num_processor, num_select)
cat_tuple = (cat_processor, cat_select)

col_transformer = make_column_transformer(num_tuple, cat_tuple, remainder='passthrough')

rf = RandomForestClassifier()

rf_pipe = make_pipeline(col_transformer, rf)

rf_pipe.fit(X_train, y_train)

rf_train_preds = rf_pipe.predict(X_train)
rf_test_preds = rf_pipe.predict(X_test)

print('train accuracy:', accuracy_score(y_train, rf_train_preds))
print('\n')
print('test accuracy:', accuracy_score(y_test, rf_test_preds))

print("Classification Report for Training Set")
print(classification_report(y_train, rf_train_preds)) # classification report to see our both train and test datasets our doing
print("\n")
print("Classification Report for Testing Set")
print(classification_report(y_test, rf_test_preds))
print("\n")
print(confusion_matrix(y_test, rf_test_preds))

"""99%"""

rf_pipe.get_params() # this is to get the parameter before we tune the model

# setting parameters by listing ranges
rf_params = {'randomforestclassifier__n_estimators': [100,300],
          'randomforestclassifier__max_depth': [5,10],
          'randomforestclassifier__min_samples_split': [2,10],
          'randomforestclassifier__min_samples_leaf': [2,10]
          }

rf_grid = GridSearchCV(rf_pipe, rf_params)
rf_grid.fit(X_train, y_train)

rf_grid.best_params_ # this is to get the best parameters

best_rf = rf_grid.best_estimator_

best_rf_train_preds = best_rf.predict(X_train)
best_rf_test_preds = best_rf.predict(X_test)
print('Best train accuracy:', accuracy_score(y_train, best_rf_train_preds))
print('\n')
print('Best test accuracy:', accuracy_score(y_test, best_rf_test_preds))
print('\n')
print("Classification Report for Best Training Set")
print(classification_report(y_train, best_rf_train_preds))
print("\n")
print("Classification Report for Best Testing Set")
print(classification_report(y_test, best_rf_test_preds))
print("\n")
print("Confusion Matrix")
print(confusion_matrix(y_test, best_rf_test_preds))

dt = DecisionTreeClassifier()

dt_pipe = make_pipeline(col_transformer, dt)

dt_pipe.fit(X_train, y_train)

dt_train_preds = dt_pipe.predict(X_train)
dt_test_preds = dt_pipe.predict(X_test)

print('train accuracy:', accuracy_score(y_train, dt_train_preds))
print('\n')
print('test accuracy:', accuracy_score(y_test, dt_test_preds))

print("Classification Report for Training Set")
print(classification_report(y_train, dt_train_preds)) # classification report to see our both train and test datasets our doing
print("\n")
print("Classification Report for Testing Set")
print(classification_report(y_test, dt_test_preds))
print("\n")
print(confusion_matrix(y_test, dt_test_preds))
print("\n")
print(confusion_matrix(y_test, dt_test_preds))

"""Decision Tree: 97%"""

from sklearn.ensemble import BaggingClassifier

bc = BaggingClassifier()

bc_pipe = make_pipeline(col_transformer, bc)

bc_pipe.fit(X_train, y_train)

bc_train_preds = bc_pipe.predict(X_train)
bc_test_preds = bc_pipe.predict(X_test)

print('train accuracy:', accuracy_score(y_train, bc_train_preds))
print('\n')
print('test accuracy:', accuracy_score(y_test, bc_test_preds))

print("Classification Report for Training Set")
print(classification_report(y_train, bc_train_preds)) # classification report to see our both train and test datasets our doing
print("\n")
print("Classification Report for Testing Set")
print(classification_report(y_test, bc_test_preds))
print("\n")
print(confusion_matrix(y_test, bc_test_preds))
print("\n")
print(confusion_matrix(y_test, bc_test_preds))

"""Bagging: 98%"""