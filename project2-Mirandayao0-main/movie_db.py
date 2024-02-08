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
            
        '''
        self.cur.execute(query)
        all_rows = self.cur.fetchall()
        return all_rows
        

    def q2(self):
        query = '''
            
        '''
        self.cur.execute(query)
        all_rows = self.cur.fetchall()
        return all_rows

    def q3(self):
        query = '''
            
        '''
        self.cur.execute(query)
        all_rows = self.cur.fetchall()
        return all_rows


    def q4(self):
        query = '''
            
        '''
        self.cur.execute(query)
        all_rows = self.cur.fetchall()
        return all_rows

    def q5(self):
        query = '''
            
        '''
        self.cur.execute(query)
        all_rows = self.cur.fetchall()
        return all_rows

    def q6(self):
        query = '''
            
        '''
        self.cur.execute(query)
        all_rows = self.cur.fetchall()
        return all_rows

    def q7(self):
        query = '''
            
        '''
        self.cur.execute(query)
        all_rows = self.cur.fetchall()
        return all_rows

    def q8(self):
        query = '''
            
        '''
        self.cur.execute(query)
        all_rows = self.cur.fetchall()
        return all_rows


    def q9(self):
        query = '''
            
        '''
        self.cur.execute(query)
        all_rows = self.cur.fetchall()
        return all_rows

    def q10(self):
        query = '''
            
        '''
        self.cur.execute(query)
        all_rows = self.cur.fetchall()
        return all_rows

    def q11(self):
        query = '''
            
        '''
        self.cur.execute(query)
        all_rows = self.cur.fetchall()
        return all_rows

    def q12(self):
        query = '''
            
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
