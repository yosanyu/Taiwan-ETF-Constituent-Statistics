import requests
import csvwriter
from bs4 import BeautifulSoup
import re
import time


class ETFRequester:
    def __init__(self, etfs):
        self.etfs = etfs
        self.callback_text = None
        self.callback_get_stock = None
        self.stock_dict = {}
        self.stock_max_weight_dict = {}
        self.stock_min_weight_dict = {}
        self.base_url = ''
        self.len = len(self.etfs)
        self.string_len = str(self.len)

    def start_request(self):
        index = 1
        for etf in self.etfs:
            url = self.base_url + etf + '.TW'
            message = '正在請求{}的成分股中... 進度 {}/{}\n'.format(etf, str(index), self.string_len)
            self.callback_text(message)
            request = requests.get(url)
            request.encoding = 'utf-8'
            soup = BeautifulSoup(request.text, "html.parser")
            weights = soup.findAll('td', 'col06')
            stock_index = 0
            for stock in soup.findAll('td', 'col05'):
                content = stock.find('a')
                text = content.get('href')
                match = re.findall('[0-9]+', text)
                # 避免抓取有誤而超出邊界
                if len(match) > 2:
                    key = match[1]
                    # 個股代號為4碼
                    if key in self.stock_dict.keys() and len(key) == 4:
                        num = self.stock_dict.get(key)
                        self.stock_dict[key] = num + 1
                    else:
                        self.stock_dict[key] = 1
                    weight = weights[stock_index].get_text()
                    self.set_weight(key, etf, weight)
                stock_index += 1
            index += 1
            # 不要頻繁請求
            time.sleep(3)
        # 根據value做降冪排序
        sort_desc = dict(sorted(self.stock_dict.items(), key=lambda x: x[1], reverse=True))
        titles = ['代號', '名稱', '次數', '百分比', '最大權重ETF', '最大權重', '最小權重ETF', '最小權重']
        write_list = [self.etfs, titles]
        for key, value in sort_desc.items():
            str_value = str(value)
            count = str_value + '/' + self.string_len
            percentage = str(round(value / self.len * 100, 2)) + '%'
            name = self.callback_get_stock(key)
            max_weight, min_weight = self.stock_max_weight_dict.get(key), self.stock_min_weight_dict.get(key)
            row = [key, name, count, percentage, max_weight[0], max_weight[1], min_weight[0], min_weight[1]]
            write_list.append(row)

        csv_write = csvwriter.CSVWriter(write_list)
        self.callback_text('output.csv文件已保存')
        self.clear()

    def set_weight(self, key, etf, weight):
        # 更新最大權重
        if key in self.stock_max_weight_dict.keys():
            max_weight = self.stock_max_weight_dict.get(key)
            if float(weight) > max_weight[1]:
                self.stock_max_weight_dict[key] = (etf, float(weight))
        else:
            self.stock_max_weight_dict[key] = (etf, float(weight))
        # 更新最小權重
        if key in self.stock_min_weight_dict.keys():
            min_weight = self.stock_min_weight_dict.get(key)
            if float(weight) < min_weight[1]:
                self.stock_min_weight_dict[key] = (etf, float(weight))
        else:
            self.stock_min_weight_dict[key] = (etf, float(weight))

    def clear(self):
        self.stock_dict = {}
        self.stock_max_weight_dict = {}
        self.stock_min_weight_dict = {}