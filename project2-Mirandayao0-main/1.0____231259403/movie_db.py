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
    def q6(self):
        query = '''
         SELECT m.title, COUNT(*) AS number_of_cast_members
            FROM Movies m
            JOIN Cast c ON m.mid = c.mid
            GROUP BY m.mid
            ORDER BY number_of_cast_members DESC, m.title
            LIMIT 10;
   
        '''
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
        WITH Bacon1 AS (
            SELECT c.aid
            FROM Cast c
            JOIN Movies m ON c.mid = m.mid
            WHERE c.mid IN (
                SELECT mid
                FROM Cast
                WHERE aid = '1011' 
            )
        ), Bacon2 AS (
            SELECT DISTINCT c.aid
            FROM Cast c
            JOIN Bacon1 ON c.mid IN (
                SELECT mid
                FROM Cast
                WHERE aid IN (SELECT aid FROM Bacon1)
            )
            WHERE c.aid NOT IN ('1011') AND c.aid NOT IN (SELECT aid FROM Bacon1)
        )
        SELECT a.fname, a.lname
        FROM Actors a
        JOIN Bacon2 ON a.aid = Bacon2.aid
        ORDER BY a.lname, a.fname;
  
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
    print(rows)
    print()
    rows = task.q1()
    print(rows)
    print()
    rows = task.q2()
    print(rows)
    print()
    rows = task.q3()
    print(rows)
    print()
    rows = task.q4()
    print(rows)
    print()
    rows = task.q5()
    print(rows)
    print()
    rows = task.q6()
    print(rows)
    print()
    rows = task.q7()
    print(rows)
    print()
    rows = task.q8()
    print(rows)
    print()
    rows = task.q9()
    print(rows)
    print()
    rows = task.q10()
    print(rows)
    print()
    rows = task.q11()
    print(rows)
    print()
    rows = task.q12()
    print(rows)
    print()
