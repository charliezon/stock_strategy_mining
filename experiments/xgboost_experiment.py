import xgboost as xgb

class XGBoostExperiment:

    def __init__(self, train_data_path, test_data_path, params=None, num_round=1000, pred_threshold=0.5):
        self._train_data_path = train_data_path
        self._test_data_path = test_data_path

        # specify parameters via map, definition are same as c++ version
        if params is None:
            self._params = {'max_depth':22, 'eta':0.1, 'silent':0, 'objective':'binary:logistic','min_child_weight':3,'gamma':14 }
        else:
            self._params = params
        
        self._num_round = num_round
        self._pred_threshold = pred_threshold

    def __call__(self):
        # read in data
        dtrain = xgb.DMatrix(self._train_data_path)
        dtest = xgb.DMatrix(self._test_data_path)

        # specify validations set to watch performance
        watchlist = [(dtest,'eval'), (dtrain,'train')]

        bst = xgb.train(self._params, dtrain, self._num_round, watchlist)

        # this is prediction
        preds = bst.predict(dtest)
        labels = dtest.get_label()
        print ('error=%f' % ( sum(1 for i in range(len(preds)) if int(preds[i]>0.5)!=labels[i]) /float(len(preds))))

        print ('correct=%f' % ( sum(1 for i in range(len(preds)) if int(preds[i]>0.5)==labels[i]) /float(len(preds))))