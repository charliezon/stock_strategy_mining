import sys
sys.path.append('../')
import os
from utils.util import write_csv, round_float
from operator import itemgetter


class BaseProcess(object):

    def __init__(self, raw_data_path, process_data_path, interested_features, need_sort=True, gen_normal=False, gen_weka=False, gen_svm=False):

        # directory storing raw data
        self._raw_data_path = raw_data_path

        # directory to store processed data
        self._process_data_path = process_data_path

        # the features that need to be extracted
        self._interested_features = interested_features

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

    def process(self):
        data = self.process_folder(self._raw_data_path)
        if self._need_sort:
            data = self.sort_data(data)

        if self._gen_normal:
            write_csv(self._process_data_path+'/data.csv', data)

        if self._gen_svm:
            self.generate_svm_data(data)

        if self._gen_weka:
            title = []
            for k in self._interested_features:
                title.append('feature' + str(k))
            title.append('success')
            data.insert(0, title)
            write_csv(self._process_data_path+'/data_weka.csv', data)

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

    def process_file(self, path):
        raise NotImplementedError

    def sort_data(self, data):
        raise NotImplementedError


class SimpleProcess(BaseProcess):
    def __init__(self, raw_data_path, process_data_path, interested_features, need_sort=True, gen_normal=False, gen_weka=False, gen_svm=False, stop_loss_rate=0.10, take_profit_rate=0.04, holding_days=30, lose_cache=0.005, num_feature=108, num_ignore=35, signal_index=101, date_index=0, open_index=1, high_index=2, low_index=3, close_index=4):

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

        super(SimpleProcess, self).__init__(raw_data_path, process_data_path, interested_features, need_sort, gen_normal, gen_weka, gen_svm)

    def process_file(self, path):
        data = []
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

    def sort_data(self, data):
        data = sorted(data, key=itemgetter(0))
        new_data = []
        for k in range(len(data)):
            new_data.append(data[k][1:])
        data = new_data
        return data