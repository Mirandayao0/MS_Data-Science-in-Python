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
        # sample query. You should change it to the correct one


    def t1(self):
        # Find the top 20 facilities that start with ‘Pitt’ and
        # have the highest counts of violations (facility name[facility], number of violations[count]).
        query = """
            SELECT facility_name AS facility, COUNT(*) AS count
            FROM "{}"
            WHERE 
            "inspect_dt" BETWEEN '{}' and '{}' AND "city" = '{}'
            and 
            facility_name LIKE 'Pitt%' 
            AND rating = 'V'
            GROUP BY facility_name
            ORDER BY count DESC
            LIMIT 20            
            """.format(self.resource_id, self.start_str, self.end_str, "Pittsburgh")
        response = requests.get(self.wprdc_api_endpoint, {'sql': query}, verify=False)
        df = pd.DataFrame.from_dict(json.loads(response.text)['result']['records'])
        return df

    def t2(self):
        # run an initial query to get the tie-breaker values
        tie_breaker_query = """
              SELECT MIN(violation_count) AS tie_breaker_value
                FROM (
                SELECT facility_name, COUNT(*) AS violation_count
                FROM "{}"
                WHERE 
                 "inspect_dt" BETWEEN '{}' and '{}' AND "city" = '{}'and rating = '{}'
                GROUP BY facility_name
                ORDER BY violation_count DESC
                LIMIT 18
                ) AS top_violations 
          """.format(self.resource_id, self.start_str, self.end_str, "Pittsburgh","V")

        # Execute the tie-breaker query
        tie_breaker_result = requests.get(self.wprdc_api_endpoint, {'sql': tie_breaker_query}, verify=False)

        # 将结果从JSON格式转换为Python字典，并提取tie-breaker value
        df = pd.DataFrame.from_dict(json.loads(tie_breaker_result.text)['result']['records'])

        # 检查DataFrame是否为空，然后提取tie-breaker value
        if not df.empty:
            tie_breaker_value = df.iloc[0]['tie_breaker_value']
        else:
            tie_breaker_value = None

        final_query = """
               SELECT facility_name AS facility, COUNT(*) AS count
               FROM "{}"
               WHERE
                 "inspect_dt" BETWEEN '{}' and '{}' AND "city" = '{}'
                 and
                rating = 'V'
               GROUP BY facility_name
               HAVING COUNT(*) >= {}
               ORDER BY count DESC
           """.format(self.resource_id, self.start_str, self.end_str, "Pittsburgh", tie_breaker_value)

        # # 假设执行SQL查询的代码在这里
        final_result = requests.get(self.wprdc_api_endpoint, {'sql': final_query},verify=False)
        # # 执行final_query并获取结果
        df = pd.DataFrame.from_dict(json.loads(final_result.text)['result']['records'])
        return df

    def t3(self):
        # run an initial query to get a dataframe of the results
        # Query to select facilities starting with 'Pitt', their violations, and facility names
        query = """
               SELECT description_new AS violation, facility_name
               FROM "{}"
               WHERE 
                "inspect_dt" BETWEEN '{}' and '{}' AND "city" = '{}'
                and 
                facility_name LIKE 'Pitt%' 
                AND rating = 'V'
                
           """.format(self.resource_id, self.start_str, self.end_str, "Pittsburgh")

        # Execute the query
        response = requests.get(self.wprdc_api_endpoint, {'sql': query}, verify=False)
        df = pd.DataFrame.from_dict(json.loads(response.text)['result']['records'])

        # # Manipulate the dataframe to group by the violation category and concatenate the facility names
        if df.empty:
            return pd.DataFrame(columns=['violation', 'count', 'facilities'])
            # Group by violation and aggregate facility names

        grouped = df.groupby('violation').agg({
            'facility_name': [
                ('count',lambda x: x.nunique()),  # Count the unique number of facility names
                ('facilities', lambda x: ', '.join(sorted(set(x))))  # Concatenate facility names
            ]
        })

        # The above groupby operation creates a MultiIndex for columns,
        # so we need to flatten the MultiIndex to get proper column names
        grouped.columns = ['count', 'facilities']
        grouped.reset_index(inplace=True)

        return grouped


    def t4(self):
        # SQL query to find categories and their risk ratings for violations at facilities with 'Pitt' as a separate word
        query = """
               SELECT 
                   facility_name AS facility,
                   description_new AS violation,
                   high,
                   medium,
                   low
               FROM "{}"
               WHERE 
                "inspect_dt" BETWEEN '{}' and '{}' AND "city" = '{}'and rating = '{}'
                and
                (facility_name LIKE 'Pitt %' OR 
                facility_name LIKE '% Pitt %' OR 
                facility_name LIKE '% Pitt')
                and
                (facility_name NOT LIKE '%Pittsburgh%')
           """.format(self.resource_id, self.start_str, self.end_str, "Pittsburgh","V")

        # Execute the query and fetch the data
        response = requests.get(self.wprdc_api_endpoint, {'sql': query}, verify=False)
        data = pd.DataFrame.from_dict(json.loads(response.text)['result']['records'])

        return data

if __name__ == "__main__":
    t = Task(date(2021, 9, 1), date(2022, 6, 1))
    # print("----T1----" + "\n")
    # print(str(t.t1()) + "\n")
    # print("----T2----" + "\n")
    # print(str(t.t2()) + "\n")
    print("----T3----" + "\n")
    print(str(t.t3()) + "\n")
    print("----T4----" + "\n")
    print(str(t.t4()) + "\n")
