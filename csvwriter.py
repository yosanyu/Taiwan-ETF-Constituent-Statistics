import csv


class CSVWriter:
    def __init__(self, rows):
        self.csv_file = 'output.csv'
        with open(self.csv_file, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerows(rows)
