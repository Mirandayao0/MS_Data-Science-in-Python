import os
from requests import get
import json
import csv
import ssl

ssl._create_default_https_context = ssl._create_unverified_context


class Task(object):
    def __init__(self):
        self.response = get('https://labrinidis.cs.pitt.edu/cs1656/data/hours.json', verify=False)
        self.hours = json.loads(self.response.content)
        # print(self.hours)
    def part4(self):
    # write output to hours.csv
        with open('hours.csv', mode='w', newline='') as file:
            writer = csv.writer(file)
            # Write the header row
            writer.writerow(['name', 'day', 'time'])
            # Iterate through each item in self.hours
            for i, item in enumerate(self.hours):
                print(i, item)
                # Extract name, day, and time and write them to the CSV
                name = item.get('name')
                day = item.get('day')
                time = item.get('time')
                # print(name, day, time)
                writer.writerow([name, day, time])



    def part5(self):
        # write output to 'part5.txt'
        output_file = open('part5.txt', 'w')
        # col_name = []
        with open('hours.csv', 'r') as csv_file:
            content = csv.reader(csv_file)
            # print(content)
            for row in content:
                print(f"{row = }")
                output_str = ','.join(row) + "\n"
                output_file.write(output_str)

        # Write the contents to 'part5.txt'
        # with open('part5.txt', 'w') as txt_file:
        #     txt_file.write(content)
        output_file.close()

    def part6(self):
        # write output to 'part6.txt'
        f = open('part6.txt', 'w')
        with open('hours.csv', 'r') as csv_file:
            reader = csv.reader(csv_file)
            rows = [row for row in reader]  # Read all rows into a list

        # Write the rows to 'part6.txt', formatted as printed on the console
        with open('part6.txt', 'w') as txt_file:
            for row in rows:
                # Convert each row to a string representation and write it
                txt_file.write(str(row))

    def part7(self):
        # write output to 'part7.txt'
        #f = open('part7.txt', 'w')
        with open('hours.csv', 'r') as csv_file:
            reader = csv.reader(csv_file)
            rows = [row for row in reader]  # Read all rows into a list

        # Write each cell to 'part7.txt' without spaces or anything between them
        with open('part7.txt', 'w') as txt_file:
            for row in rows:
                for cell in row:
                    txt_file.write(cell)


if __name__ == '__main__':
    task = Task()

    task.part4()
    task.part5()
    task.part6()
    task.part7()