#!/bin/env python3

# ML model application
# Reference : MachinelearningHEP
##  processer.py : applymodel
##  models.py : apply

import xgboost as xgb
import pandas as pd
import numpy as np
import pickle, lz4.frame
import matplotlib.pyplot as plt

dataDir = '/mnt/d/MLHEP/DsJet/MLapplication/skpkldecmerged/'
dataFileName = 'AnalysisResultsReco2_4_0.30.pkl.lz4'
dataSaveName = 'RecoML_pt_cand2_4.pkl.lz4'
modelDir = '/mnt/d/MLHEP/DsJet/mlout/'
modelName = 'Model_pT_2_4.model'
modelType = 'xgboost'
ml_probcut_presel = 0.3
ml_probcut_optimal = 0.985
ml_probcut = ml_probcut_optimal

var_training = ['d_len', 'd_len_xy', 'norm_dl_xy', 'cos_p', 'cos_p_xy', 'imp_par_xy', 'sig_vert', 'delta_mass_KK', 'cos_PiKPhi_3', 'max_norm_d0d0exp', 'nsigComb_Pi_0', 'nsigComb_K_0', 'nsigComb_Pi_1', 'nsigComb_K_1', 'nsigComb_Pi_2', 'nsigComb_K_2']

def load_model(modelPath : str, features : list):
  model = None
  if(modelPath.endswith('.model')):
    model = xgb.XGBClassifier()
    model.load_model(modelPath)
    model._Booster.feature_names = features
  elif(modelPath.endswith('.sav')):
    try:
      model = pickle.load(open(modelPath,'rb'))
    except ValueError:
      print(f'[X] Error - incomptible XGBoost version, fail to load model ({modelPath})')
      exit()
  else:
    print('[X] Error - unrecognized model format')
    exit()
  print(f'[-] Model loaded with features : {repr(model._Booster.feature_names)}')
  return model

df = pickle.load(lz4.frame.open(dataDir+dataFileName,'rb')) # DataFrame
bdt = load_model(modelDir+modelName, var_training) # XGBClassifier
model = xgb.XGBClassifier()

## ADD columns of ML classification
x_values = df[var_training]
# BDT prediction result (False=0 / True=1)
y_test_prediction = bdt.predict(x_values)
y_test_prediction = y_test_prediction.reshape(len(y_test_prediction),)
df['y_test_prediction'+modelType] = pd.Series(y_test_prediction, index=df.index)
# BDT prediction prob. (0.00 - 1.00)
y_test_prob = bdt.predict_proba(x_values)
df['y_test_prob'+modelType] = pd.Series(y_test_prob[:, 1], index=df.index)


# ML selection - prob. cut
probvar = "y_test_prob" + modelType
df = df.loc[df[probvar] > ml_probcut_presel]

# Output
pickle.dump(df, lz4.frame.open(dataDir+dataSaveName,'wb'), protocol=4)

