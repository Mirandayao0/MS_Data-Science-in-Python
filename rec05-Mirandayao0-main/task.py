import json
from datetime import datetime, timedelta, date
import requests
import pandas as pd

class Task(object):
    def __init__(self, start_date, end_date):
        self.wprdc_api_endpoint = "https://data.wprdc.org/api/3/action/datastore_search_sql"
        self.resource_id = "1a1329e2-418c-4bd3-af2c-cc334e7559af"
        self.start_str = start_date.strftime("%Y-%m-%d")
        self.end_str = end_date.strftime("%Y-%m-%d")        

    def t1(self):
        # sample query. You should change it to the correct one
        query = """
            SELECT *
            FROM "{}"
            WHERE "inspect_dt" BETWEEN '{}' and '{}' AND "city" = '{}'
            LIMIT 30 """.format(self.resource_id, self.start_str, self.end_str, "Pittsburgh")
        response = requests.get(self.wprdc_api_endpoint, {'sql': query}, verify=False)
        df = pd.DataFrame.from_dict(json.loads(response.text)['result']['records'])
        return df

    def t2(self):
        # run an initial query to get the tie-breaker values
        
        # use the tie-breaker value to construct the final query and return the results
        return None

    def t3(self):
        # run an initial query to get a dataframe of the results
        
        # manilulate the dataframe to group the results by the violation category and concatenate the facility names
        return None

    def t4(self):
        return None

if __name__ == "__main__":
    t = Task(date(2021, 9, 1), date(2022, 6, 1))
    print("----T1----" + "\n")
    print(str(t.t1()) + "\n")
    print("----T2----" + "\n")
    print(str(t.t2()) + "\n")
    print("----T3----" + "\n")
    print(str(t.t3()) + "\n")
    print("----T4----" + "\n")
    print(str(t.t4()) + "\n")
