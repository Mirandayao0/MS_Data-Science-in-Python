import sqlite3 as lite
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
import sqlite3
import sys
import time
import xml


class Movie_db(object):
    def __init__(self, db_name):
        #db_name: "cs1656-public.db"
        self.con = lite.connect(db_name)
        self.cur = self.con.cursor()
    
    #q0 is an example 
    def q0(self):
        query = '''SELECT COUNT(*) FROM Actors'''
        self.cur.execute(query)
        all_rows = self.cur.fetchall()
        return all_rows

    def q1(self):
        query = '''
            SELECT DISTINCT a.fname, a.lname
            FROM Actors a
            JOIN Cast c ON c.aid = a.aid
            JOIN Movies m ON c.mid = m.mid
            WHERE (m.year BETWEEN 1980 AND 1990)
            AND a.aid IN (
                SELECT c2.aid
                FROM Cast c2
                JOIN Movies m2 ON c2.mid = m2.mid
                WHERE m2.year >= 2000)
                ORDER BY a.lname, a.fname;
 
        '''
        self.cur.execute(query)
        all_rows = self.cur.fetchall()
        return all_rows
        

    def q2(self):
        query = '''
            SELECT m.title, m.year
            FROM Movies m
            WHERE m.year = (
                SELECT year
                FROM Movies
                WHERE title = 'Rogue One: A Star Wars Story'
            ) AND m.rank > (
                SELECT rank
                FROM Movies
                WHERE title = 'Rogue One: A Star Wars Story'
            )
            ORDER BY m.title;
 
        '''
        self.cur.execute(query)
        all_rows = self.cur.fetchall()
        return all_rows

    #  Actors in Star Wars Movies
    def q3(self):
        query = '''
        SELECT a.fname, a.lname, COUNT(DISTINCT m.mid) AS number_of_movies
        FROM Actors a
        JOIN Cast c ON a.aid = c.aid
        JOIN Movies m ON c.mid = m.mid
        WHERE m.title LIKE '%Star Wars%'
        GROUP BY a.aid
        ORDER BY number_of_movies DESC, a.lname, a.fname;
   
        '''
        self.cur.execute(query)
        all_rows = self.cur.fetchall()
        return all_rows

    # Actors Only in Films Before 1990
    def q4(self):
        query = '''
        SELECT a.fname, a.lname
        FROM Actors a
        WHERE NOT EXISTS (
            SELECT 1
            FROM Cast c
            JOIN Movies m ON c.mid = m.mid
            WHERE a.aid = c.aid AND m.year >= 1990
        )
        AND EXISTS (
            SELECT 1
            FROM Cast c
            JOIN Movies m ON c.mid = m.mid
            WHERE a.aid = c.aid AND m.year < 1990
        )
        ORDER BY a.lname, a.fname;
    
        '''
        self.cur.execute(query)
        all_rows = self.cur.fetchall()
        return all_rows

    # Top 10 Directors by Number of Films
    def q5(self):
        query = '''
        SELECT d.fname, d.lname, COUNT(*) AS number_of_films
            FROM Directors d
            JOIN Movie_Director md ON d.did = md.did
            GROUP BY d.did
            ORDER BY number_of_films DESC, d.lname, d.fname
            LIMIT 10;
   
        '''
        self.cur.execute(query)
        all_rows = self.cur.fetchall()
        return all_rows

    #  Top 10 Movies by Largest Cast
    # def q6(self):
        # query='''
        # SELECT m.title, COUNT(c.aid) AS number_of_cast_members
        #     FROM Movies m
        #     JOIN Cast c ON m.mid = c.mid
        #     GROUP BY m.title
        #     HAVING COUNT(c.aid) >= (
        #     SELECT COUNT(c2.aid)
        #     FROM Cast c2
        #     JOIN Movies m2 ON c2.mid = m2.mid
        #     GROUP BY c2.mid
        #     ORDER BY COUNT(c2.aid) DESC
        #     LIMIT 1 OFFSET 9
        #     )
        #     ORDER BY COUNT(c.aid) DESC, m.title;
        #
        # '''
        # self.cur.execute(query)
        # all_rows = self.cur.fetchall()
        # return all_rows
    
    def q6(self):
        threshold_query = """
        SELECT MIN(number_of_cast_members) AS threshold
        FROM (
        SELECT COUNT(*) AS number_of_cast_members
        FROM Cast
        GROUP BY mid
        ORDER BY COUNT(*) DESC
        LIMIT 10
        ) AS SubQuery;
        """
        self.cur.execute(threshold_query)
    # We use fetchone() since we're only selecting one record (the 10th largest cast count)
        threshold = self.cur.fetchone()[0]
        print(threshold)
      
       
    # Step 2: Find all movies with a number of cast members at or above the threshold
        query = f"""
        SELECT m.title, COUNT(c.aid) AS number_of_cast_members
        FROM Movies m
        JOIN Cast c ON m.mid = c.mid
        GROUP BY m.mid
        HAVING COUNT(c.aid) >= {threshold}
        ORDER BY COUNT(c.aid) DESC, m.title;
        """
    
        self.cur.execute(query)
        all_rows = self.cur.fetchall()
        return all_rows

    # Movies with More Actors than Actresses
    def q7(self):
        query = '''
         SELECT m.title, 
            SUM(CASE WHEN a.gender = 'Male' THEN 1 ELSE 0 END) AS number_of_actors,
            SUM(CASE WHEN a.gender = 'Female' THEN 1 ELSE 0 END) AS number_of_actresses
        FROM Movies m
        JOIN Cast c ON m.mid = c.mid
        JOIN Actors a ON c.aid = a.aid
        GROUP BY m.mid
        HAVING number_of_actors > number_of_actresses
        ORDER BY m.title;
   
        '''
        self.cur.execute(query)
        all_rows = self.cur.fetchall()
        return all_rows

    # Actors Who Worked with at Least 7 Different Directors
    def q8(self):
        query = '''
         SELECT a.fname, a.lname, COUNT(DISTINCT md.did) AS number_of_directors
            FROM Actors a
            JOIN Cast c ON a.aid = c.aid
            JOIN Movie_Director md ON c.mid = md.mid
            JOIN Directors d ON md.did = d.did
            WHERE NOT EXISTS (
                SELECT 1 FROM Directors d2 WHERE d2.did = d.did AND d2.fname = a.fname AND d2.lname = a.lname
            )
            GROUP BY a.aid
            HAVING COUNT(DISTINCT md.did) >= 7
            ORDER BY number_of_directors DESC, a.lname, a.fname;
   
        '''
        self.cur.execute(query)
        all_rows = self.cur.fetchall()
        return all_rows


    def q9(self):
        query = '''
         SELECT a.fname, a.lname, COUNT(m.mid) AS debut_year_movie_count
            FROM Actors a
            JOIN Cast c ON a.aid = c.aid
            JOIN Movies m ON c.mid = m.mid
            WHERE a.fname LIKE 'B%'
            AND m.year = (
                SELECT MIN(m2.year)
                FROM Movies m2
                JOIN Cast c2 ON m2.mid = c2.mid
                WHERE c2.aid = a.aid
            )
            GROUP BY a.aid
            ORDER BY debut_year_movie_count DESC, a.lname, a.fname;
   
        '''
        self.cur.execute(query)
        all_rows = self.cur.fetchall()
        return all_rows

    def q10(self):
        query = '''
         SELECT a.lname, m.title
            FROM Actors a
            JOIN Cast c ON a.aid = c.aid
            JOIN Movies m ON c.mid = m.mid
            JOIN Movie_Director md ON m.mid = md.mid
            JOIN Directors d ON md.did = d.did
            WHERE a.lname = d.lname AND a.fname <> d.fname
            ORDER BY a.lname, m.title;
   
        '''
        self.cur.execute(query)
        all_rows = self.cur.fetchall()
        return all_rows

    def q11(self):
        query = '''
            SELECT DISTINCT a2.fname, a2.lname
                FROM Actors a1
                JOIN Cast c1 ON a1.aid = c1.aid
                JOIN Movies m1 ON c1.mid = m1.mid
                JOIN Cast c2 ON m1.mid = c2.mid
                JOIN Actors a2 ON c2.aid = a2.aid
                WHERE a1.aid IN (
                SELECT c3.aid
                FROM Cast c3
                JOIN Movies m2 ON c3.mid = m2.mid
                JOIN Cast c4 ON m2.mid = c4.mid
                WHERE c4.aid = (SELECT aid FROM Actors WHERE fname = 'Kevin' AND lname = 'Bacon')
                ) AND a2.aid NOT IN (
                SELECT aid FROM Actors WHERE fname = 'Kevin' AND lname = 'Bacon'
                ) AND a2.aid NOT IN (
                SELECT c5.aid
                FROM Cast c5
                JOIN Movies m3 ON c5.mid = m3.mid
                JOIN Cast c6 ON m3.mid = c6.mid
                WHERE c6.aid = (SELECT aid FROM Actors WHERE fname = 'Kevin' AND lname = 'Bacon')
                )
                ORDER BY a2.lname, a2.fname;

  
        '''
        self.cur.execute(query)
        all_rows = self.cur.fetchall()
        return all_rows

    def q12(self):
        query = '''
        SELECT a.fname, a.lname, COUNT(m.mid) AS total_movies, AVG(m.rank) AS popularity_score
        FROM Actors a
        JOIN Cast c ON a.aid = c.aid
        JOIN Movies m ON c.mid = m.mid
        GROUP BY a.aid
        ORDER BY AVG(m.rank) DESC, total_movies DESC
        LIMIT 20;
 
        '''
        self.cur.execute(query)
        all_rows = self.cur.fetchall()
        return all_rows

if __name__ == "__main__":
    task = Movie_db("cs1656-public.db")
    rows = task.q0()
    # print(rows)
    # print()
    # rows = task.q1()
    # print(rows)
    # print()
    # rows = task.q2()
    # print(rows)
    # print()
    # rows = task.q3()
    # print(rows)
    # print()
    # rows = task.q4()
    # print(rows)
    # print()
    # rows = task.q5()
    # print(rows)
    # print()
    rows = task.q6()
    print(rows)
    print()
    # rows = task.q7()
    # print(rows)
    # print()
    # rows = task.q8()
    # print(rows)
    # print()
    # rows = task.q9()
    # print(rows)
    # print()
    # rows = task.q10()
    # print(rows)
    # print()
    # rows = task.q11()
    # print(rows)
    # print()
    # rows = task.q12()
    # print(rows)
    # print()
