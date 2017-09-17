#!/usr/bin/env python3
# -*- coding: utf-8 -*-

''' Process raw data and extract features.

    Only process *follow* signal. (#102)

    Sort the extracted data.
'''
import sys
sys.path.append('../../')
from experiments.common_process import BigIndexProcess

if __name__ == "__main__":
    process = BigIndexProcess(
        'F:/项目/StockMining/data_for_dl/data/data_buy_follow_index_1/raw',
        './data/processed',
        'F:/项目/StockMining/data_for_dl/data/data_buy_follow_index_1/999999.txt',
        'F:/项目/StockMining/data_for_dl/data/data_buy_follow_index_1/399001.txt',
        gen_weka=True,
        gen_svm=True,
        signal_index=102,
        take_profit_rate=0.034
        )
    process()