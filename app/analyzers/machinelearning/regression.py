from app.analyzers.machinelearning.mlutils import ModelUtil
from xgboost import XGBRegressor
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import Ridge
from sklearn.linear_model import Lasso
from sklearn.neighbors import KNeighborsRegressor
from sklearn.svm import SVR
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.ensemble import AdaBoostRegressor
from sklearn.ensemble import GradientBoostingRegressor


class Regression():
    def linear_regression(self, x, y, x_test, predict=False, cv_times=5):
        """Linear Regression model

        Args:
            x (pandas.DataFrame): Features to fit the model.
            y (pandas.DataFrame): Target variable to fit the model.
            x_test (pandas.DataFrame): New features dataset to predict results.
            predict (binary, optional): Defaults to False. Use the model to see results or do prediction.
            cv_times(int, optional): Defaults to 5. Cross validation k-fold times.

        Returns:
            pandas.DataFrame: A dataframe contains predicted results.
            or
            list: A list contains performance matrices.
        """
        lr_reg = LinearRegression()
        if predict == False:
            util = ModelUtil()
            results = util.cross_validation_score(lr_reg, x, y, cv_times)
        else:
            lr_model = lr_reg.fit(x, y)
            results = lr_model.predict(x_test)
        return results

    def ridge_regression(self, x, y, x_test, predict=False, cv_times=5):
        """Ridge Regression model

        Args:
            x (pandas.DataFrame): Features to fit the model.
            y (pandas.DataFrame): Target variable to fit the model.
            x_test (pandas.DataFrame): New features dataset to predict results.
            predict (binary, optional): Defaults to False. Use the model to see results or do prediction.
            cv_times(int, optional): Defaults to 5. Cross validation k-fold times.

        Returns:
            pandas.DataFrame: A dataframe contains predicted results.
            or
            list: A list contains performance matrices.
        """
        ri_reg = Ridge()
        if predict == False:
            util = ModelUtil()
            results = util.cross_validation_score(ri_reg, x, y, cv_times)
        else:
            ri_model = ri_reg.fit(x, y)
            results = ri_model.predict(x_test)
        return results

    def lasso_regression(self, x, y, x_test, predict=False, cv_times=5):
        """Lasso Regression model

        Args:
            x (pandas.DataFrame): Features to fit the model.
            y (pandas.DataFrame): Target variable to fit the model.
            x_test (pandas.DataFrame): New features dataset to predict results.
            predict (binary, optional): Defaults to False. Use the model to see results or do prediction.
            cv_times(int, optional): Defaults to 5. Cross validation k-fold times.

        Returns:
            pandas.DataFrame: A dataframe contains predicted results.
            or
            list: A list contains performance matrices.
        """
        la_reg = Lasso()
        if predict == False:
            util = ModelUtil()
            results = util.cross_validation_score(la_reg, x, y, cv_times)
        else:
            la_model = la_reg.fit(x, y)
            results = la_model.predict(x_test)
        return results

    def knn_regression(self, x, y, x_test, predict=False, cv_times=5):
        """K Nearest Neighbour model

        Args:
            x (pandas.DataFrame): Features to fit the model.
            y (pandas.DataFrame): Target variable to fit the model.
            x_test (pandas.DataFrame): New features dataset to predict results.
            predict (binary, optional): Defaults to False. Use the model to see results or do prediction.
            cv_times (int, optional): Defaults to 5. Cross validation k-fold times.

        Returns:
            pandas.DataFrame: A dataframe contains predicted results.
            or
            list: A list contains performance matrices.
        """
        knn_reg = KNeighborsRegressor(n_neighbors=4)
        if predict == False:
            util = ModelUtil()
            results = util.cross_validation_score(knn_reg, x, y, cv_times)
        else:
            knn_model = knn_reg.fit(x, y)
            results = knn_model.predict(x_test)
        return results

    def svr_regression(self, x, y, x_test, predict=False, cv_times=5):
        """Support Vector Regression model

        Args:
            x (pandas.DataFrame): Features to fit the model.
            y (pandas.DataFrame): Target variable to fit the model.
            x_test (pandas.DataFrame): New features dataset to predict results.
            predict (binary, optional): Defaults to False. Use the model to see results or do prediction.
            cv_times (int, optional): Defaults to 5. Cross validation k-fold times.

        Returns:
            pandas.DataFrame: A dataframe contains predicted results.
            or
            list: A list contains performance matrices.
        """
        knn_reg = SVR(kernel="poly", C=100, gamma="auto", degree=3, epsilon=0.1, coef0=1)
        if predict == False:
            util = ModelUtil()
            results = util.cross_validation_score(knn_reg, x, y, cv_times)
        else:
            knn_model = knn_reg.fit(x, y)
            results = knn_model.predict(x_test)
        return results

    def dt_regression(self, x, y, x_test, predict=False, cv_times=5):
        """Decision Tree Regression model

        Args:
            x (pandas.DataFrame): Features to fit the model.
            y (pandas.DataFrame): Target variable to fit the model.
            x_test (pandas.DataFrame): New features dataset to predict results.
            predict (binary, optional): Defaults to False. Use the model to see results or do prediction.
            cv_times (int, optional): Defaults to 5. Cross validation k-fold times.

        Returns:
            pandas.DataFrame: A dataframe contains predicted results.
            or
            list: A list contains performance matrices.
        """
        dt_reg = DecisionTreeRegressor()
        if predict == False:
            util = ModelUtil()
            results = util.cross_validation_score(dt_reg, x, y, cv_times)
        else:
            dt_model = dt_reg.fit(x, y)
            results = dt_model.predict(x_test)
        return results

    def rf_regression(self, x, y, x_test, predict=False, cv_times=5):
        """Random Forest Regression model

        Args:
            x (pandas.DataFrame): Features to fit the model.
            y (pandas.DataFrame): Target variable to fit the model.
            x_test (pandas.DataFrame): New features dataset to predict results.
            predict (binary, optional): Defaults to False. Use the model to see results or do prediction.
            cv_times (int, optional): Defaults to 5. Cross validation k-fold times.

        Returns:
            pandas.DataFrame: A dataframe contains predicted results.
            or
            list: A list contains performance matrices.
        """
        rf_reg = RandomForestRegressor(n_estimators=100, max_features=10, n_jobs=-1, random_state=42)
        if predict == False:
            util = ModelUtil()
            results = util = ModelUtil().cross_validation_score(rf_reg, x, y, cv_times)
        else:
            rf_model = rf_reg.fit(x, y)
            results = rf_model.predict(x_test)
        return results

    def et_regression(self, x, y, x_test, predict=False, cv_times=5):
        """Extra Tree Regression model

        Args:
            x (pandas.DataFrame): Features to fit the model.
            y (pandas.DataFrame): Target variable to fit the model.
            x_test (pandas.DataFrame): New features dataset to predict results.
            predict (binary, optional): Defaults to False. Use the model to see results or do prediction.
            cv_times (int, optional): Defaults to 5. Cross validation k-fold times.

        Returns:
            pandas.DataFrame: A dataframe contains predicted results.
            or
            list: A list contains performance matrices.
        """
        et_reg = ExtraTreesRegressor(n_estimators=100, random_state=42)
        if predict == False:
            util = ModelUtil()
            results = util.cross_validation_score(et_reg, x, y, cv_times)
        else:
            et_model = et_reg.fit(x, y)
            results = et_model.predict(x_test)
        return results

    def adb_regression(self, x, y, x_test, predict=False, cv_times=5):
        """Adaboosting Regression model

        Args:
            x (pandas.DataFrame): Features to fit the model.
            y (pandas.DataFrame): Target variable to fit the model.
            x_test (pandas.DataFrame): New features dataset to predict results.
            predict (binary, optional): Defaults to False. Use the model to see results or do prediction.
            cv_times (int, optional): Defaults to 5. Cross validation k-fold times.

        Returns:
            pandas.DataFrame: A dataframe contains predicted results.
            or
            list: A list contains performance matrices.
        """
        adb_reg = AdaBoostRegressor(n_estimators=100, random_state=42)
        if predict == False:
            util = ModelUtil()
            results = util.cross_validation_score(adb_reg, x, y, cv_times)
        else:
            adb_model = adb_reg.fit(x, y)
            results = adb_model.predict(x_test)
        return results

    def gb_regression(self, x, y, x_test, predict=False, cv_times=5):
        """Gradient Boosting Regression model

        Args:
            x (pandas.DataFrame): Features to fit the model.
            y (pandas.DataFrame): Target variable to fit the model.
            x_test (pandas.DataFrame): New features dataset to predict results.
            predict (binary, optional): Defaults to False. Use the model to see results or do prediction.
            cv_times (int, optional): Defaults to 5. Cross validation k-fold times.

        Returns:
            pandas.DataFrame: A dataframe contains predicted results.
            or
            list: A list contains performance matrices.
        """
        gb_reg = GradientBoostingRegressor(random_state=42)
        if predict == False:
            util = ModelUtil()
            results = util.cross_validation_score(gb_reg, x, y, cv_times)
        else:
            gb_model = gb_reg.fit(x, y)
            results = gb_model.predict(x_test)
        return results

    def xgb_regression(self, x, y, x_test, predict=False, cv_times=5):
        """Extreme Gradient Boosting Regression model

        Args:
            x (pandas.DataFrame): Features to fit the model.
            y (pandas.DataFrame): Target variable to fit the model.
            x_test (pandas.DataFrame): New features dataset to predict results.
            predict (binary, optional): Defaults to False. Use the model to see results or do prediction.
            cv_times (int, optional): Defaults to 5. Cross validation k-fold times.

        Returns:
            pandas.DataFrame: A dataframe contains predicted results.
            or
            list: A list contains performance matrices.
        """
        xgb_reg = XGBRegressor(objective ='reg:squarederror',n_estimators = 100, random_state=42)
        if predict == False:
            util = ModelUtil()
            results = util.cross_validation_score(xgb_reg, x, y, cv_times)
        else:
            xgb_model = xgb_reg.fit(x, y)
            results = xgb_model.predict(x_test)
        return results



