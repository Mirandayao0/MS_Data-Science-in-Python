import pandas as pd
import csv
from requests import get
import json
from datetime import datetime, timedelta, date
import numpy as np
from scipy.spatial.distance import euclidean, cityblock, cosine
from scipy.stats import pearsonr

import csv
import re
import pandas as pd
import argparse
import collections
import json
import glob
import math
import os
import requests
import string
import sys
import time
import xml
import random

class Recommender(object):
    def __init__(self, training_set, test_set):
        if isinstance(training_set, str):
            # the training set is a file name
            self.training_set = pd.read_csv(training_set)
        else:
            # the training set is a DataFrame
            self.training_set = training_set.copy()

        if isinstance(test_set, str):
            # the test set is a file name
            self.test_set = pd.read_csv(test_set)
        else:
            # the test set is a DataFrame
            self.test_set = test_set.copy()
    
    def train_user_euclidean(self, data_set, userId):
        # print("debug")
        # here sample  userId = '0331949b45', is among small_test.csv 1st one, (distance is 0 to itself)
        # how to deal nan
        targetEntry =  data_set[userId].to_numpy()
        myDict = {}
        iCol = 0
        for column in data_set:    # skip first column, TBD, smarter way do so
            iCol = iCol + 1
            if iCol > 1:
                iterEntry = data_set[column].to_numpy()
                # cal happen here, note no cal for nan number
                euclidDistance = 0
                for i in range(  len(targetEntry) ):
                    if (np.isnan( targetEntry[i]) == False) and (np.isnan( iterEntry[i])== False):
                        euclidDistance = euclidDistance + ( targetEntry[i] -iterEntry[i] )**2
                euclidDistance = euclidDistance ** 0.5
                myDict[column] = 1/(1+euclidDistance)    # distance to similarity

        return myDict # dictionary of weights mapped to users. e.g. {"0331949b45":1.0, "1030c5a8a9":2.5}
    
    def train_user_manhattan(self, data_set, userId):
        # print("debug")
        # here sample  userId = '0331949b45', is among small_test.csv 1st one, (distance is 0 to itself)
        # how to deal nan
        targetEntry = data_set[userId].to_numpy()
        myDict = {}
        iCol = 0
        for column in data_set:  # skip first column, TBD, smarter way do so
            iCol = iCol + 1
            if iCol > 1:
                iterEntry = data_set[column].to_numpy()
                # cal happen here, note no cal for nan number
                euclidDistance = 0
                for i in range(len(targetEntry)):
                    if (np.isnan(targetEntry[i]) == False) and (np.isnan(iterEntry[i]) == False):
                        euclidDistance = euclidDistance + abs(targetEntry[i] - iterEntry[i])

                myDict[column] =  1/(1+euclidDistance)


        return myDict

    def train_user_cosine(self, data_set, userId):
        # print("debug")
        # here sample  userId = '0331949b45', is among small_test.csv 1st one, (distance is 0 to itself)
        # how to deal nan
        targetEntry = data_set[userId].to_numpy()
        myDict = {}
        iCol = 0
        for column in data_set:  # skip first column, TBD, smarter way do so
            iCol = iCol + 1
            if iCol > 1:
                iterEntry = data_set[column].to_numpy()
                # cal happen here, note no cal for nan number
                upperVal = 0
                LowerLeftVal = 0
                LowerRightVal = 0
                for i in range(len(targetEntry)):
                    if (np.isnan(targetEntry[i]) == False) and (np.isnan(iterEntry[i]) == False):
                        upperVal = upperVal + targetEntry[i]* iterEntry[i]
                        LowerLeftVal =  LowerLeftVal +  targetEntry[i]**2
                        LowerRightVal = LowerRightVal + iterEntry[i]**2
                LowerSum = (LowerLeftVal ** 0.5 * LowerRightVal ** 0.5)
                if LowerSum == 0:
                    myDict[column] = 1   #  "1" mean exact the same, note it direct go for similiarity
                else:
                    myDict[column] = upperVal/LowerSum
        return myDict
   
    def train_user_pearson(self, data_set, userId):
        # print("debug")
        # here sample  userId = '0331949b45', is among small_test.csv 1st one, (distance is 0 to itself)
        # how to deal nan
        targetEntry = data_set[userId].to_numpy()
        targetEntry_mean = np.mean( targetEntry[~ np.isnan( targetEntry)])
        myDict = {}
        iCol = 0
        for column in data_set:  # skip first column, TBD, smarter way do so
            iCol = iCol + 1
            if iCol > 1:
                iterEntry = data_set[column].to_numpy()
                # cal happen here, note no cal for nan number
                iterEntry_mean = np.mean(iterEntry[~ np.isnan(iterEntry)])
                upperVal = 0
                LowerLeftVal = 0
                LowerRightVal = 0
                for i in range(len(targetEntry)):
                    if (np.isnan(targetEntry[i]) == False) and (np.isnan(iterEntry[i]) == False):
                        targetEntry_delta = targetEntry[i] - targetEntry_mean
                        iterEntry_delta = iterEntry[i] - iterEntry_mean

                        upperVal = upperVal + targetEntry_delta* iterEntry_delta
                        LowerLeftVal =  LowerLeftVal +  targetEntry_delta**2
                        LowerRightVal = LowerRightVal + iterEntry_delta**2
                LowerSum = (LowerLeftVal ** 0.5 * LowerRightVal ** 0.5)
                if LowerSum == 0:
                    myDict[column] = 1   #  "1" mean exact the same, note it direct go for similiarity
                else:
                    myDict[column] = upperVal/LowerSum
        return myDict

    def train_user(self, data_set, distance_function, userId):
        if distance_function == 'euclidean':
            return self.train_user_euclidean(data_set, userId)
        elif distance_function == 'manhattan':
            return self.train_user_manhattan(data_set, userId)
        elif distance_function == 'cosine':
            return self.train_user_cosine(data_set, userId)
        elif distance_function == 'pearson':
            return self.train_user_pearson(data_set, userId)
        else:
            return None

    def get_user_existing_ratings(self, data_set, userId):
        result = []
        movieIdEntry = data_set["movieId"].to_numpy()
        targetEntry = data_set[userId].to_numpy()
        for i in range(len(movieIdEntry)):
            result.append(  (movieIdEntry[i], targetEntry[i]) )


        return result # list of tuples with movieId and rating. e.g. [(32, 4.0), (50, 4.0)]

    def predict_user_existing_ratings_top_k(self, data_set, sim_weights, userId, k):
        # sort dict by similiaty
        sim_weights_sorted = dict(sorted(sim_weights.items(), key=lambda item: item[1], reverse = True))   # need to kick off 1st one, itself
        predResult = []

        movieIdEntry = data_set["movieId"].to_numpy()

        for i in range(len(movieIdEntry)):
            predRating = 0
            kCount = 0
            for key in sim_weights_sorted:
                kCount = kCount + 1
                if key != userId  and kCount <= k+1:   # only use first-K user (not include itself),  # TBD, what if other user rating is null? =>  not adapted
                    otherEntry = data_set[key].to_numpy()
                    predRating = predRating + sim_weights_sorted[key]* otherEntry[i]
                    # print(predRating)
            predResult.append(  (movieIdEntry[i], predRating) )


        return predResult # list of tuples with movieId and rating. e.g. [(32, 4.0), (50, 4.0)]
    
    def evaluate(self, existing_ratings, predicted_ratings):
        rmse = 0
        ratio = 0
        temp = 0
        N = len(existing_ratings)
        nCount = 0
        nValidExist = 0

        for i in range( N ):
            if np.isnan(existing_ratings[i][1]) == False:
                nValidExist = nValidExist+1
            if np.isnan(existing_ratings[i][1]) == False and  np.isnan(predicted_ratings[i][1]) == False:
                nCount = nCount+1
                temp = temp + (existing_ratings[i][1] - predicted_ratings[i][1])**2
        rmse = (temp/nCount)**0.5
        ratio = nCount/ nValidExist
        result={}
        result['rmse']=rmse
        result['ratio']=ratio
        # print('ratio')
        # print(f"{result = }")
        return result    # dictionary with an rmse value and a ratio. e.g. {'rmse':1.2, 'ratio':0.5}
    
    def single_calculation(self, distance_function, userId, k_values):
        user_existing_ratings = self.get_user_existing_ratings(self.test_set, userId)
        print("User has {} existing and {} missing movie ratings".format(len(user_existing_ratings), len(self.test_set) - len(user_existing_ratings)), file=sys.stderr)

        print('Building weights')
        sim_weights = self.train_user(self.training_set[self.test_set.columns.values.tolist()], distance_function, userId)  # direct get similarity here

        result = []
        for k in k_values:
            print('Calculating top-k user prediction with k={}'.format(k))
            top_k_existing_ratings_prediction = self.predict_user_existing_ratings_top_k(self.test_set, sim_weights, userId, k)
            eva = self.evaluate(user_existing_ratings, top_k_existing_ratings_prediction)
            # print(f"{eva =}")
            result.append((k, eva))
        print(f"{result = }")
        return result # list of tuples, each of which has the k value and the result of the evaluation. e.g. [(1, {'rmse':1.2, 'ratio':0.5}), (2, {'rmse':1.0, 'ratio':0.9})]

    def aggregate_calculation(self, distance_functions, userId, k_values):
        print()
        result_per_k = {}
        for func in distance_functions:
            print("Calculating for {} distance metric".format(func))
            for calc in self.single_calculation(func, userId, k_values):
                if calc[0] not in result_per_k:
                    result_per_k[calc[0]] = {}
                result_per_k[calc[0]]['{}_rmse'.format(func)] = calc[1]['rmse']
                result_per_k[calc[0]]['{}_ratio'.format(func)] = calc[1]['ratio']
            print()
        result = []
        for k in k_values:
            row = {'k':k}
            row.update(result_per_k[k])
            result.append(row)
        columns = ['k']
        for func in distance_functions:
            columns.append('{}_rmse'.format(func))
            columns.append('{}_ratio'.format(func))
        result = pd.DataFrame(result, columns=columns)
        return result
        
if __name__ == "__main__":
    recommender = Recommender("data/train.csv", "data/small_test.csv")
    print("Training set has {} users and {} movies".format(len(recommender.training_set.columns[1:]), len(recommender.training_set)))
    print("Testing set has {} users and {} movies".format(len(recommender.test_set.columns[1:]), len(recommender.test_set)))

    result = recommender.aggregate_calculation(['euclidean', 'cosine', 'pearson', 'manhattan'], "0331949b45", [1, 2, 3, 4])
    print(result)