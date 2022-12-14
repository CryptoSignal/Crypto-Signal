This branch is designed to create some machine learning functions in the technical analysis part of this project, which could be used to preprocess and run both regression and classification analysis on the crypto data. 

We created a machine learning folder under the analyzers including the following part:

In the preprocessing.py, we defined functions to clean the data and show correlation matrix.
In the classification.py, we defined a classification class with 10 classification models, including random forest, knn, naive bayes
etc. 
In the regression.py, we defined a regression class with 11 regression models, including linear regression, svr regression, etc. 
In the mlutils.py, we defined useful utilities related to machine learning, including conducting cross validation, analyzing feature importance, etc.

We also added a test.py which implement pytest fixture to generate some test cases for our models.

How to use:
Users can easily choose any models they want from the 21 machine learning functions we created. For example, if users want to use the random forest model on their dataset, they need to firstly call the preprocessing class to clean the dataset, then they can call the random forest function in the classification class to run the model. They can customize parameters such as cv times as they want. Furthermore, they can even do tuning through our mlutils class, using cross_validation to balance results or feature_importance to see dominant features.
