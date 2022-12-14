from sklearn.naive_bayes import BernoulliNB
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import LinearSVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.ensemble import AdaBoostClassifier
from sklearn.ensemble import GradientBoostingClassifier
import xgboost as xgb
from app.analyzers.machinelearning.mlutils import ModelUtil

class Classification():
    def naive_bayes(self, x, y, x_new, predict=False, cv_times=5):
        """Naive_Bayes model

        Args:
            x (pandas.DataFrame): Features to fit the model.
            y (pandas.DataFrame): Target variable to fit the model.
            x_new (pandas.DataFrame): New features dataset to predict results.
            predict (binary, optional): Defaults to False. Use the model to see results or do prediction.
            cv_times(int, optional): Defaults to 5. Cross validation k-fold times.

        Returns:
            pandas.DataFrame: A dataframe contains predicted results.
            or
            list: A list contains performance matrices.
        """
        bnb_clf = BernoulliNB()
        if predict == False:
            util = ModelUtil()
            results = util.cross_validation_score(bnb_clf, x, y, cv_times)
        else:
            bnb_model = bnb_clf.fit(x, y)
            results = bnb_model.predict(x_new)
        return results


    def logistic_regression(self, x, y, x_new, predict=False, cv_times=5):
        """Logistic_Regression model

        Args:
            x (pandas.DataFrame): Features to fit the model.
            y (pandas.DataFrame): Target variable to fit the model.
            x_new (pandas.DataFrame): New features dataset to predict results.
            predict (binary, optional): Defaults to False. Use the model to see results or do prediction.
            cv_times(int, optional): Defaults to 5. Cross validation k-fold times.

        Returns:
            pandas.DataFrame: A dataframe contains predicted results.
            or
            list: A list contains performance matrices.
        """
        lr_clf = LogisticRegression()
        if predict == False:
            util=ModelUtil()
            results = util.cross_validation_score( lr_clf, x, y, cv_times)
        else:
            lr_model =  lr_clf.fit(x, y)
            results = lr_model.predict(x_new)
        return results


    def knn(self, x, y, x_new, predict=False, cv_times=5):
        """KNN model

        Args:
            x (pandas.DataFrame): Features to fit the model.
            y (pandas.DataFrame): Target variable to fit the model.
            x_new (pandas.DataFrame): New features dataset to predict results.
            predict (binary, optional): Defaults to False. Use the model to see results or do prediction.
            cv_times(int, optional): Defaults to 5. Cross validation k-fold times.

        Returns:
            pandas.DataFrame: A dataframe contains predicted results.
            or
            list: A list contains performance matrices.
        """
        knn_clf = KNeighborsClassifier(n_neighbors=5)
        if predict == False:
            util = ModelUtil()
            results = util.cross_validation_score(knn_clf, x, y, cv_times)
        else:
            knn_model = knn_clf.fit(x, y)
            results = knn_model.predict(x_new)
        return results

    def svc(self, x, y, x_new, predict=False, cv_times=5):
        """SVC model

        Args:
            x (pandas.DataFrame): Features to fit the model.
            y (pandas.DataFrame): Target variable to fit the model.
            x_new (pandas.DataFrame): New features dataset to predict results.
            predict (binary, optional): Defaults to False. Use the model to see results or do prediction.
            cv_times(int, optional): Defaults to 5. Cross validation k-fold times.

        Returns:
            pandas.DataFrame: A dataframe contains predicted results.
            or
            list: A list contains performance matrices.
        """
        svc_clf = LinearSVC()
        if predict == False:
            util = ModelUtil()
            results = util.cross_validation_score(svc_clf, x, y, cv_times)
        else:
            svc_model = svc_clf.fit(x, y)
            results = svc_model.predict(x_new)
        return results

    def decision_tree(self, x, y, x_new, predict=False, cv_times=5):
        """Decision_Tree model

        Args:
            x (pandas.DataFrame): Features to fit the model.
            y (pandas.DataFrame): Target variable to fit the model.
            x_new (pandas.DataFrame): New features dataset to predict results.
            predict (binary, optional): Defaults to False. Use the model to see results or do prediction.
            cv_times(int, optional): Defaults to 5. Cross validation k-fold times.

        Returns:
            pandas.DataFrame: A dataframe contains predicted results.
            or
            list: A list contains performance matrices.
        """
        dt_clf = DecisionTreeClassifier()
        if predict == False:
            util = ModelUtil()
            results =util.cross_validation_score(dt_clf, x, y, cv_times)
        else:
            dt_model = dt_clf.fit(x, y)
            results = dt_model.predict(x_new)
        return results

    def random_forest(self, x, y, x_new, predict=False, cv_times=5):
        """Rondom_Forest model

        Args:
            x (pandas.DataFrame): Features to fit the model.
            y (pandas.DataFrame): Target variable to fit the model.
            x_new (pandas.DataFrame): New features dataset to predict results.
            predict (binary, optional): Defaults to False. Use the model to see results or do prediction.
            cv_times(int, optional): Defaults to 5. Cross validation k-fold times.

        Returns:
            pandas.DataFrame: A dataframe contains predicted results.
            or
            list: A list contains performance matrices.
        """
        rf_clf = RandomForestClassifier()
        if predict == False:
            util = ModelUtil()
            results = util.cross_validation_score(rf_clf, x, y, cv_times)
        else:
            rf_model = rf_clf.fit(x, y)
            results = rf_model.predict(x_new)
        return results

    def extra_tree(self, x, y, x_new, predict=False, cv_times=5):
        """Extra_Tree model

        Args:
            x (pandas.DataFrame): Features to fit the model.
            y (pandas.DataFrame): Target variable to fit the model.
            x_new (pandas.DataFrame): New features dataset to predict results.
            predict (binary, optional): Defaults to False. Use the model to see results or do prediction.
            cv_times(int, optional): Defaults to 5. Cross validation k-fold times.

        Returns:
            pandas.DataFrame: A dataframe contains predicted results.
            or
            list: A list contains performance matrices.
        """
        et_clf = ExtraTreesClassifier()
        if predict == False:
            util = ModelUtil()
            results = util.cross_validation_score(et_clf, x, y, cv_times)
        else:
            et_model = et_clf.fit(x, y)
            results = et_model.predict(x_new)
        return results

    def adaboost(self, x, y, x_new, predict=False, cv_times=5):
        """AdaBoost model

        Args:
            x (pandas.DataFrame): Features to fit the model.
            y (pandas.DataFrame): Target variable to fit the model.
            x_new (pandas.DataFrame): New features dataset to predict results.
            predict (binary, optional): Defaults to False. Use the model to see results or do prediction.
            cv_times(int, optional): Defaults to 5. Cross validation k-fold times.

        Returns:
            pandas.DataFrame: A dataframe contains predicted results.
            or
            list: A list contains performance matrices.
        """
        ab_clf = AdaBoostClassifier()
        if predict == False:
            util = ModelUtil()
            results = util.cross_validation_score(ab_clf, x, y, cv_times)
        else:
            ab_model = ab_clf.fit(x, y)
            results = ab_model.predict(x_new)
        return results

    def gradientboosting(self, x, y, x_new, predict=False, cv_times=5):
        """GradientBoosting model

        Args:
            x (pandas.DataFrame): Features to fit the model.
            y (pandas.DataFrame): Target variable to fit the model.
            x_new (pandas.DataFrame): New features dataset to predict results.
            predict (binary, optional): Defaults to False. Use the model to see results or do prediction.
            cv_times(int, optional): Defaults to 5. Cross validation k-fold times.

        Returns:
            pandas.DataFrame: A dataframe contains predicted results.
            or
            list: A list contains performance matrices.
        """
        gb_clf = GradientBoostingClassifier()
        if predict == False:
            util = ModelUtil()
            results = util.cross_validation_score(gb_clf, x, y, cv_times)
        else:
            gb_model = gb_clf.fit(x, y)
            results = gb_model.predict(x_new)
        return results

    def xgboost(self, x, y, x_new, predict=False, cv_times=5):
        """XGBoost model

        Args:
            x (pandas.DataFrame): Features to fit the model.
            y (pandas.DataFrame): Target variable to fit the model.
            x_new (pandas.DataFrame): New features dataset to predict results.
            predict (binary, optional): Defaults to False. Use the model to see results or do prediction.
            cv_times(int, optional): Defaults to 5. Cross validation k-fold times.

        Returns:
            pandas.DataFrame: A dataframe contains predicted results.
            or
            list: A list contains performance matrices.
        """
        xgb_clf = xgb.XGBClassifier()
        if predict == False:
            util = ModelUtil()
            results = util.cross_validation_score(xgb_clf, x, y, cv_times)
        else:
            xgb_model = xgb_clf.fit(x, y)
            results = xgb_model.predict(x_new)
        return results

