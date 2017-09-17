import sys
sys.path.append('../')
import os
from utils.util import write_csv, round_float
from operator import itemgetter

class BaseProcess(object):

    def __init__(self, raw_data_path, process_data_path, need_sort=True, gen_normal=False, gen_weka=False, gen_svm=False):

        # directory storing raw data
        self._raw_data_path = raw_data_path

        # directory to store processed data
        self._process_data_path = process_data_path

        # whether to sort the data according to the first feature (date)
        self._need_sort = need_sort

        # whether generate data
        self._gen_normal = gen_normal

        # whether generate weka format data
        self._gen_weka = gen_weka

        # whether generate svm format data
        self._gen_svm = gen_svm

    def process_folder(self, path):
        path = os.path.abspath(path)
        data = []
        for x in os.listdir(path):
            new_path = os.path.join(path, x)
            if os.path.isdir(new_path):
                data[0:0] = self.process_folder(new_path)
            elif os.path.isfile(new_path) and os.path.splitext(x)[1]=='.txt':
                print(new_path)
                data[0:0] = self.process_file(new_path)
        return data


    def process_file(self, path):
        raise NotImplementedError

    def sort_data(self, data):
        raise NotImplementedError

    def generate_svm_data(self, data):
        new_data = []
        for item in data:
            data_item = []
            data_item.append(str(item[len(item)-1]));
            for i in range(len(item)-1):
                data_item.append(str(i+1) + ':' + str(item[i]))
            new_data.append(' '.join(data_item))

        def write_file(path, data):
            with open(path, 'w') as f:
                f.write(data)

        data_len = len(new_data)
        train_len = int(data_len*0.9)
        train_data = new_data[0:train_len]
        test_data = new_data[train_len:]

        write_file(self._process_data_path + '/train_data_svm.txt', '\n'.join(train_data))
        write_file(self._process_data_path + '/test_data_svm.txt', '\n'.join(test_data))

    def generate_weka_data(self, data):
        raise NotImplementedError

    def __call__(self):
        data = self.process_folder(self._raw_data_path)
        if self._need_sort:
            data = self.sort_data(data)

        if self._gen_normal:
            write_csv(self._process_data_path+'/data.csv', data)

        if self._gen_svm:
            self.generate_svm_data(data)

        if self._gen_weka:
            self.generate_weka_data(data)

    def sort_data(self, data):
        data = sorted(data, key=itemgetter(0))
        new_data = []
        for k in range(len(data)):
            new_data.append(data[k][1:])
        data = new_data
        return data

class SimpleProcess(BaseProcess):
    def __init__(self, raw_data_path, process_data_path, need_sort=True, gen_normal=False, gen_weka=False, gen_svm=False, stop_loss_rate=0.10, take_profit_rate=0.04, holding_days=30, lose_cache=0.005, num_feature=108, num_ignore=35, signal_index=101, date_index=0, open_index=1, high_index=2, low_index=3, close_index=4):

        # the rate for stopping loss
        self._stop_loss_rate = stop_loss_rate

        # the rate for taking profit
        self._take_profit_rate = take_profit_rate

        # the maximum holding dates of the stock
        self._holding_days = holding_days

        # a cache for stopping loss
        self._lose_cache = lose_cache

        # the number of column of features
        self._num_feature = num_feature

        # the number of lines of data to be ignored
        self._num_ignore = num_ignore

        # buy or follow signal (buy: 101, follow:102)
        self._signal_index = signal_index

        self._date_index = date_index

        self._open_index = open_index

        self._high_index = high_index

        self._low_index = low_index

        self._close_index = close_index

        super(SimpleProcess, self).__init__(raw_data_path, process_data_path, need_sort, gen_normal, gen_weka, gen_svm)

    def judge_success(self, content):
        data = []
        for i in range(len(content)):
            if i + self._holding_days + 1 < len(content) and content[i][4] == 1:
                new_open_price = content[i+1][1]
                win_price = round_float(new_open_price * (1+self._take_profit_rate), 4)
                lose_price = round_float(new_open_price * (1-self._stop_loss_rate+self._lose_cache), 4)
                success = 0
                for j in range(i+2, i + self._holding_days + 2):
                    new_high_price = content[j][2]
                    new_low_price = content[j][3]
                    if new_low_price <= lose_price:
                        success = 0
                        break
                    if new_high_price >= win_price:
                        success = 1
                        break
                data_item = []
                if self._need_sort:
                    data_item.append(content[i][0])
                data_item.extend(content[i][5:])
                data_item.append(success)
                data.append(data_item)
        return data

class InterestProcess(SimpleProcess):

    def __init__(self, raw_data_path, process_data_path, interested_features, need_sort=True, gen_normal=False, gen_weka=False, gen_svm=False, stop_loss_rate=0.10, take_profit_rate=0.04, holding_days=30, lose_cache=0.005, num_feature=108, num_ignore=35, signal_index=101, date_index=0, open_index=1, high_index=2, low_index=3, close_index=4):

        # the features that need to be extracted
        self._interested_features = interested_features

        super(InterestProcess, self).__init__(raw_data_path, process_data_path, need_sort, gen_normal, gen_weka, gen_svm, stop_loss_rate, take_profit_rate, holding_days, lose_cache, num_feature, num_ignore, signal_index, date_index, open_index, high_index, low_index, close_index)

    def generate_weka_data(self, data):
        title = []
        for k in self._interested_features:
            title.append('feature' + str(k))
        title.append('success')
        data.insert(0, title)
        write_csv(self._process_data_path+'/data_weka.csv', data)

    def process_file(self, path):
        content = []
        with open(path, 'r') as f:
            i = 0
            # ignore the first *num_ignore* lines of data
            for line in f.readlines():
                line_data = line.strip().split('\t')
                if i > self._num_ignore and len(line_data) == self._num_feature:
                    item = []
                    item.append(line_data[self._date_index].strip())
                    item.append(float(line_data[self._open_index].strip()))
                    item.append(float(line_data[self._high_index].strip()))
                    item.append(float(line_data[self._low_index].strip()))
                    item.append(int(float(line_data[self._signal_index].strip())))
                    for j in self._interested_features:
                        if line_data[j].strip() == '':
                            item.append(-999)
                        elif j == self._date_index:
                            item.append(line_data[j].strip())
                        else:
                            item.append(float(line_data[j].strip()))
                    content.append(item)
                i += 1
        return self.judge_success(content)

class BigIndexProcess(SimpleProcess):

    def __init__(self, raw_data_path, process_data_path, shanghai_index_path, shenzhen_index_path, winner_index=7, turnover_index=70, increase_index=39, need_sort=True, gen_normal=False, gen_weka=False, gen_svm=False, stop_loss_rate=0.10, take_profit_rate=0.04, holding_days=30, lose_cache=0.005, num_feature=108, num_ignore=35, signal_index=101, date_index=0, open_index=1, high_index=2, low_index=3, close_index=4):

        self._shanghai_index_path = shanghai_index_path
        self._shenzhen_index_path = shenzhen_index_path
        self._shanghai_data = process_index(shanghai_index_path)
        self._shenzhen_data = process_index(shenzhen_index_path)
        self._shanghai_date_list = sorted(self._shanghai_data.keys())
        self._shenzhen_date_list = sorted(self._shenzhen_data.keys())

        self._winner_index = winner_index
        self._turnover_index = turnover_index
        self._increase_index = increase_index

        super(BigIndexProcess, self).__init__(raw_data_path, process_data_path, need_sort, gen_normal, gen_weka, gen_svm, stop_loss_rate, take_profit_rate, holding_days, lose_cache, num_feature, num_ignore, signal_index, date_index, open_index, high_index, low_index, close_index)

    def generate_weka_data(self, data):
        if len(data)>0:
            title = []
            for k in range(len(data[0])-1):
                title.append('feature' + str(k))
            title.append('success')
            data.insert(0, title)
            write_csv(self._process_data_path+'/data_weka.csv', data)

    def process_file(self, path):
        content = []
        with open(path, 'r') as f:
            i = 0
            # ignore the first *num_ignore* lines of data
            for line in f.readlines():
                line_data = line.strip().split('\t')
                if i > self._num_ignore and len(line_data) == self._num_feature:
                    date = line_data[self._date_index].strip()
                    winner = line_data[self._winner_index].strip()
                    winner = float(winner) if winner!='' else None
                    turnover = line_data[self._turnover_index].strip()
                    turnover = float(turnover) if turnover!='' else None
                    increase = line_data[self._increase_index].strip()
                    increase = float(increase) if increase!='' else None

                    if date in self._shanghai_date_list and date in self._shenzhen_date_list:
                        pre_date = self._shanghai_date_list[self._shanghai_date_list.index(date) - 1]
                        if not (pre_date in self._shanghai_date_list and pre_date in self._shenzhen_date_list):
                            continue
                    else:
                        continue

                    item = []
                    item.append(date)
                    item.append(float(line_data[self._open_index].strip()))
                    item.append(float(line_data[self._high_index].strip()))
                    item.append(float(line_data[self._low_index].strip()))
                    item.append(int(float(line_data[self._signal_index].strip())))

                    e1 = (date in self._shanghai_data) and (self._shanghai_data[date][4]>self._shanghai_data[date][8])
                    item.append(int(e1))
                    e2 = (date in self._shenzhen_data) and (self._shenzhen_data[date][4]>self._shenzhen_data[date][8])
                    item.append(int(e2))
                    e3 = self._shanghai_data[pre_date][1]+self._shanghai_data[pre_date][4]<=self._shanghai_data[date][1]+self._shanghai_data[date][4] and self._shenzhen_data[pre_date][1]+self._shenzhen_data[pre_date][4]<=self._shenzhen_data[date][1]+self._shenzhen_data[date][4]
                    item.append(int(e3))
                    e4 = self._shanghai_data[date][4]>self._shanghai_data[date][1] and self._shenzhen_data[date][4]>self._shenzhen_data[date][1] and self._shanghai_data[date][4]>max(self._shanghai_data[pre_date][1], self._shanghai_data[pre_date][4]) and self._shenzhen_data[date][4]>max(self._shenzhen_data[pre_date][1], self._shenzhen_data[pre_date][4])
                    item.append(int(e4))

                    e5 = winner is not None and winner > 0.9
                    item.append(int(e5))
                    e6 = winner is not None and winner > 0.6 and winner <= 0.9
                    item.append(int(e6))
                    e7 = winner is not None and winner > 0.3 and winner <= 0.6
                    item.append(int(e7))
                    e8 = winner is not None and winner > 0.25 and winner <= 0.3
                    item.append(int(e8))
                    e9 = winner is not None and winner > 0.2 and winner <= 0.25
                    item.append(int(e9))
                    e10 = winner is not None and winner > 0.15 and winner <= 0.2
                    item.append(int(e10))
                    e11 = winner is not None and winner > 0.1 and winner <= 0.15
                    item.append(int(e11))
                    e12 = winner is not None and winner > 0.05 and winner <= 0.1
                    item.append(int(e12))
                    e13 = winner is not None and winner >= 0 and winner <= 0.05
                    item.append(int(e13))

                    e14 = turnover is not None and turnover <= 0.005
                    item.append(int(e14))
                    e15 = turnover is not None and turnover > 0.005 and turnover <= 0.01
                    item.append(int(e15))
                    e16 = turnover is not None and turnover > 0.01 and turnover <= 0.03
                    item.append(int(e16))
                    e17 = turnover is not None and turnover > 0.03 and turnover <= 0.05
                    item.append(int(e17))
                    e18 = turnover is not None and turnover > 0.05 and turnover <= 0.10
                    item.append(int(e18))
                    e19 = turnover is not None and turnover > 0.10 and turnover <= 0.20
                    item.append(int(e19))
                    e20 = turnover is not None and turnover > 0.20
                    item.append(int(e20))

                    e21 = increase is not None and increase <= 0
                    item.append(int(e21))
                    e22 = increase is not None and increase > 0 and increase <= 0.02
                    item.append(int(e22))
                    e23 = increase is not None and increase > 0.02 and increase <= 0.04
                    item.append(int(e23))
                    e24 = increase is not None and increase > 0.04 and increase <= 0.06
                    item.append(int(e24))
                    e25 = increase is not None and increase > 0.06 and increase <= 0.09
                    item.append(int(e25))
                    e26 = increase is not None and increase > 0.09
                    item.append(int(e26))

                    content.append(item)
                i += 1
        return self.judge_success(content)

def process_index(path):
    data = {}
    content = []
    with open(path, 'r') as f:
        i = 0
        # 前35行数据不要
        for line in f.readlines():
            line_data = line.strip().split('\t')
            if i > 35 and len(line_data) == 10:
                item = []
                item.append(line_data[0].strip())
                for j in range(1, len(line_data)):
                    if line_data[j].strip() == '':
                        item.append(None)
                    else:
                        item.append(float(line_data[j].strip()))
                content.append(item)
            i += 1

    for i in range(len(content)):
        date = content[i][0]
        open_price = content[i][1]
        high_price = content[i][2]
        low_price = content[i][3]
        close_price = content[i][4]
        volume = content[i][5]

        ma1 = content[i][6]
        ma2 = content[i][7]
        ma3 = content[i][8]
        ma4 = content[i][9]

        data_item = []
        data_item.append(date)
        data_item.append(open_price)
        data_item.append(high_price)
        data_item.append(low_price)
        data_item.append(close_price)
        data_item.append(volume)
        data_item.append(ma1)
        data_item.append(ma2)
        data_item.append(ma3)
        data_item.append(ma4)

        data[date] = data_item
    return data


