import sklearn as sk
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
        bnb_clf = sk.BernoulliNB()
        if predict == False:
            results = ModelUtil.cross_validation_score(bnb_clf, x, y, cv_times)
        else:
            bnb_model = bnb_clf.fit(x, y)
            results = bnb_model.predict(x_new)
        return results
