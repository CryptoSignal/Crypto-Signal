import pandas as pd
from sklearn.model_selection import cross_val_score, cross_validate
import matplotlib.pyplot as plt
import statsmodels.formula.api as smf

class ModelUtil():
    def cross_validation_score(self, estimator, x, y, cv_times=5, classification=True):
        """Choose cross validation model

        Args:
            estimator (string): Estimator name.
            x (pandas.DataFrame): Features to fit the model.
            y (pandas.DataFrame): Target variable to fit the model.
            cv_times(int, optional): Defaults to 5. Cross validation k-fold times.
            classification(binary,optional): Defaults to true. Determined choosing regression
                or classification model.
        Returns:
            list: A list contains performance matrices.
        """
        if classification == False:
            results = self.regression_cross_validation_score(estimator, x, y, cv_times)
        else:
            results = self.classification_cross_validation_score(estimator, x, y, cv_times)
        return results

    def classification_cross_validation_score(self, classifier, x, y, cv_times=5):
        """Do cross validation

        Args:
            classifier (string): Classifier name.
            x (pandas.DataFrame): Features to fit the model.
            y (pandas.DataFrame): Target variable to fit the model.
            cv_times(int): Defaults to 5. Cross validation k-fold times.

        Returns:
            list: A list contains performance matrices.
        """

        results = []
        name = classifier.__class__.__name__.split('.')[-1]

        recall = cross_val_score(estimator=classifier, X=x, y=y, cv=cv_times, scoring='recall')
        f1 = cross_val_score(estimator=classifier, X=x, y=y, cv=cv_times, scoring='f1')
        auc = cross_val_score(estimator=classifier, X=x, y=y, cv=cv_times, scoring='roc_auc')
        results.append([name, recall.mean(), f1.mean(), auc.mean()])

        return results

    def regression_cross_validation_score(self, regressor, x, y, cv_times=5):
        """Do cross validation

        Args:
            regressor (string): Regressor name.
            x (pandas.DataFrame): Features to fit the model.
            y (pandas.DataFrame): Target variable to fit the model.
            cv_times(int): Defaults to 5. Cross validation k-fold times.

        Returns:
            list: A list contains performance matrices.
        """

        results = []
        name = regressor.__class__.__name__.split('.')[-1]

        r2 = cross_val_score(estimator=regressor, X=x, y=y, cv=cv_times, scoring='r2')
        results.append([name, r2.mean()])

        return results

    def feature_importance(self, classifier, x, y, cv_times=5):
        """Calculate feature importance under cross validation

        Args:
            classifier (string): Classifier name.
            x (pandas.DataFrame): Features to fit the model.
            y (pandas.DataFrame): Target variable to fit the model.
            cv_times(int): Defaults to 5. Cross validation k-fold times.

        Returns:
            list: A list contains mean feature importance.
        """
        importance_array = []
        mean_importance = []

        models = cross_validate(estimator=classifier, X=x, y=y, cv=cv_times, return_estimator=True)
        for i in range(cv_times):
            importance = models['estimator'][i].feature_importances_
            importance_array.append(importance)
        for j in range(x.shape[1]):
            temp = 0
            for i in range(cv_times):
                temp = temp + importance_array[i][j]
            mean_importance.append(temp / cv_times)
        return mean_importance

    def plot_importance(self, index_array, importance):
        """Show important features under cross validation

        Args:
            index_array (list): Features name list.
            importance (list): Feature importance list.

        Returns:
            None
        """
        feature_importance = pd.Series(importance, index=index_array)
        feature_importance = feature_importance.sort_values(ascending=False)
        feature_importance = feature_importance[:8]
        fig = plt.figure(figsize=(12, 5))
        plt.bar(feature_importance.index, feature_importance.values, color="blue")
        plt.xlabel('features')
        plt.ylabel('importance')
        plt.show()

    def forward_select(self, x, y):
        """Forward select important feature under AIC metric

        Args:
            x (pandas.DataFrame): Features to fit the model. Also features being selected from.
            y (pandas.DataFrame): Target variable to fit the model.

        Returns:
            sklearn.model: A new model after forward selection.
        """
        data = pd.concat([x, y], axis=1)
        variate = set(x.columns)
        selected = []
        # set the scores to be infinite
        current_score, best_new_score = float('inf'), float('inf')
        # perform the forward selection
        while variate:
            aic_with_variate = []
            for candidate in variate:
                # set the regression model
                formula = "{}~{}".format(y.columns[0], "+".join(selected + [candidate]))
                aic = smf.ols(formula=formula, data=data).fit().aic
                aic_with_variate.append((aic, candidate))
            aic_with_variate.sort(reverse=True)
            best_new_score, best_candidate = aic_with_variate.pop()
            if current_score > best_new_score:
                variate.remove(best_candidate)
                selected.append(best_candidate)
                current_score = best_new_score
                print("AIC is {}, continuing!".format(current_score))
            else:
                print("Forward Selection Done")
                break
        # final regression model
        formula = "{}~{}".format(y.columns[0], "+".join(selected))
        print("Final Regression model is {}".format(formula))
        model = smf.ols(formula=formula, data=data).fit()
        return (model)