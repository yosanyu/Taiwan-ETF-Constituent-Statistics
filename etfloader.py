import os
import csv


class ETFLoader:
    def __init__(self):
        self.etf_issuer = []
        self.etf_code = []
        self.etf_name = []
        self.load_csv()

    def load_csv(self):
        project_path = os.getcwd()
        path = project_path + '\\etfissuer'
        os.chdir(path)
        files = os.listdir()
        code = []
        name = []
        for file in files:
            with open(file, newline='', encoding="utf-8") as csvfile:
                rows = csv.reader(csvfile)
                for row in rows:
                    code.append(row[0])
                    name.append(row[1])
            filename, file_extension = os.path.splitext(file)
            self.etf_issuer.append(filename)
            self.etf_code.append(code)
            self.etf_name.append(name)
            code = []
            name = []
        os.chdir(project_path)

    def get_title(self, index):
        titles = []
        size = len(self.etf_code[index])
        for i in range(size):
            title = self.etf_code[index][i] + ' ' + self.etf_name[index][i]
            titles.append(title)
        return titles
