#!/usr/bin/env python3
# -*- coding: utf-8 -*-

''' Process raw data and extract the following features:
    * Profit rate of current day (#7)
    * Increase rate of current day (#39)
    * Turnover rate of current day (#70)

    Only process *buy* signal.  (#101)

    Sort the extracted data.
'''
import sys
sys.path.append('../../')
from experiments.common_process import SimpleProcess

if __name__ == "__main__":
    process = SimpleProcess(
        'F:/项目/StockMining/data_for_dl/data/data_buy_follow_index_1/raw',
        './data/processed',
        [7, 39, 70],
        gen_svm=True
        )
    process()