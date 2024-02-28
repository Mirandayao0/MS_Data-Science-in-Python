import json
from datetime import datetime, timedelta
import requests
import pandas as pd
import numpy as np
from scipy.spatial.distance import euclidean, cityblock, cosine

import ssl
ssl._create_default_https_context = ssl._create_unverified_context

class Task(object):
    def __init__(self, data):
        self.df = pd.read_csv(data)
        # self.visualize_all_column_names()
        # print(is_matrix)
    """
    For a specified user, calculate ALL missing movie ratings using user-based recommendation with Cosine Similarity Metric. 
    Please note that scipy.spatial.distance.cosine() returns the cosine distance, not the cosine similarity. 
    You need to convert it properly to the similarity metric. It is trivial if you look at the formulas for cosine distance and similarity.
    """

    def visualize_all_column_names(self):
        values = self.all_user_names()
        for i, value in enumerate(values):
            print(f"Col.{i:02d} : {value}")
    
    
    def all_user_names(self, exclude=None):
        if exclude is None:
            return self.df.columns.values
        elif isinstance(exclude, list):
            return [i for i in self.df.columns.values if not i in exclude]
        else:
            return [i for i in self.df.columns.values if not i == exclude]


    def cosine_similarity(self, vector1, vector2):
        # print(f"{vector1 = }")
        # print(f"{vector2 = }")
        return 1 - cosine(vector1, vector2)
    
    
    def t1(self, name):
        specified_user = name
        # df = self.df.replace(r'^\s*$', np.nan, regex=True)
        df = self.df
        # Calculate similarities with all users
        similarities = {}
        other_user_names = self.all_user_names(exclude=[specified_user, 'Alias'])
        for user_name in other_user_names:
            common_movies = df[specified_user].notnull() & df[user_name].notnull()
            # print(f"{common_movies = }")
            similarities[user_name] = self.cosine_similarity(df.loc[common_movies, specified_user], df.loc[common_movies, user_name])
        print(f"{similarities = }")
        # Predict ratings for each movie
        movies_not_rated_by_specified_user = df['Alias'][df[specified_user].isnull()]
        print(f"Movies not rated by specified user:\n{movies_not_rated_by_specified_user}")
        # print(f"{other_user_names = }")
        all_missing_movie_ratings = [] ## it should be a list of (str, np.float64)
                                       ## which is [(movie_name_0, rating_0), (movie_name_1, rating_1)]
        
        for movie in movies_not_rated_by_specified_user:
            # row = df.loc[df['Alias'] == movie]
            movie_grades = df.loc[df['Alias'] == movie, other_user_names].iloc[0] ## .iloc[0] is important!
            # movie_has_grade = movie_grades.notnull()
            # print(f"{movie_rated}")
            weighted_sum = np.nan
            sum_weights = 0
            for other_user_name in other_user_names:
                grade = movie_grades[other_user_name]
                if pd.isnull(grade):
                    continue
                if not other_user_name in similarities.keys():
                    continue
                weighted_grade = grade * similarities[other_user_name]
                sum_weights += similarities[other_user_name]
                if weighted_sum is np.nan :
                    weighted_sum = 0.0 + weighted_grade
                else:
                    weighted_sum += weighted_grade
                
                # print(movie, other_user_name, grade, weighted_grade)
            final_grade = weighted_sum / sum_weights
            print(movie, final_grade)
            all_missing_movie_ratings.append((movie, final_grade))
        return all_missing_movie_ratings
        


    def t2(self, user_name):
        # Transpose DataFrame for item-based approach
        df_transposed = self.df.set_index('Alias').transpose()
        # Ensure user exists in transposed DataFrame
        if user_name not in df_transposed.index:
            raise ValueError(f"User {user_name} not found in DataFrame")
        # print(f"{self.df[user_name]}")
        
        # Extract all movies rated by the user
        user_ratings = df_transposed.loc[user_name].dropna()
        
        # Find all movies not rated by the user
        movies_not_rated = set(self.df['Alias']) - set(user_ratings.index)
        # print(f"{movies_not_rated = }")
        # Initialize a list to store the predicted ratings
        predicted_ratings = []
        
        for movie in movies_not_rated:
            # Collect all user ratings for the current movie
            current_movie_ratings = self.df.set_index('Alias').loc[movie].dropna()
            
            # Initialize variables to calculate weighted sum of ratings
            weighted_sum = 0
            sum_of_weights = 0
            
            for rated_movie in user_ratings.index:
                # Collect all user ratings for a movie the user has rated
                rated_movie_ratings = self.df.set_index('Alias').loc[rated_movie].dropna()
                
                # Calculate similarity between the current movie and the rated movie
                common_users = list(set(current_movie_ratings.index) & set(rated_movie_ratings.index))
                # print(f"{current_movie_ratings[list(common_users)] = }")
                if len(common_users) > 0:
                    similarity = self.cosine_similarity(current_movie_ratings[common_users], rated_movie_ratings[common_users])
                    weighted_sum += similarity * user_ratings[rated_movie]
                    sum_of_weights += similarity
            
                # print(weighted_sum, sum_of_weights)
            # Calculate predicted rating if sum_of_weights is not 0
            if sum_of_weights > 0:
                predicted_rating = weighted_sum / sum_of_weights
                predicted_ratings.append((movie, predicted_rating))
            else:
                predicted_ratings.append((movie, None))
        
        return predicted_ratings
    def t3(self, name):
        specified_user = name
        df = self.df
        # Calculate similarities with all users
        similarities = {}
        other_user_names = self.all_user_names(exclude=[specified_user, 'Alias'])
        for user_name in other_user_names:
            common_movies = df[specified_user].notnull() & df[user_name].notnull()
            if common_movies.any():
                similarities[user_name] = self.cosine_similarity(df.loc[common_movies, specified_user], df.loc[common_movies, user_name])
        
        # Sort similarities and select top 10
        top_10_similar_users = sorted(similarities, key=similarities.get, reverse=True)[:10]
        
        # Predict ratings for each movie not rated by the specified user
        movies_not_rated_by_specified_user = df['Alias'][df[specified_user].isnull()]
        all_missing_movie_ratings = []
        
        for movie in movies_not_rated_by_specified_user:
            movie_grades = df.loc[df['Alias'] == movie, top_10_similar_users].iloc[0]
            weighted_sum = 0
            sum_weights = 0
            for other_user_name in top_10_similar_users:
                grade = movie_grades[other_user_name]
                if pd.isnull(grade) or other_user_name not in similarities:
                    continue
                weighted_grade = grade * similarities[other_user_name]
                sum_weights += similarities[other_user_name]
                weighted_sum += weighted_grade
            
            if sum_weights > 0:
                final_grade = weighted_sum / sum_weights
                all_missing_movie_ratings.append((movie, final_grade))
            else:
                all_missing_movie_ratings.append((movie, None))
        
        return all_missing_movie_ratings
    

if __name__ == "__main__":
    # using the class movie ratings data we collected in http://data.cs1656.org/movie_class_responses.csv
    # t = Task('http://data.cs1656.org/movie_class_responses.csv')
    t = Task('movie_class_responses.csv')
    print(t.t1('BabyKangaroo'))
    print('------------------------------------')
    print(t.t2('BabyKangaroo'))
    print('------------------------------------')
    print(t.t3('BabyKangaroo'))
    print('------------------------------------')