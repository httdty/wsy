# -*- coding: utf-8 -*-
# @Time    : 2021/2/5 15:20
# @Author  : Ray
# @Email   : httdty2@163.com
# @File    : Stat.py
# @Software: PyCharm


import json
import os
import pandas as pd
import jieba


DATA_DIR = '../Data/'


def formatted(json_path: str):
    with open(json_path, 'r') as f:  # 打开文件
        raw_data = json.load(f)  # 加载json
    raw_data = raw_data.get('data', {})  # 获取真正的data
    return [danmu for cid in raw_data for date in raw_data[cid] for danmu in raw_data[cid][date]]  # 拼接全部弹幕


def get_bvid(json_path: str):
    return json_path.split('/')[-1][:-5]  # 获取BV号


def get_all_json():
    all_json = list()  # 全部json文件路径
    key_word_list = os.listdir(DATA_DIR)  # 获取全部关键字
    if '.DS_Store' in key_word_list:  # 删除mac系统自带的.DS_Store文件
        key_word_list.remove('.DS_Store')
    for key in key_word_list:
        key_path = DATA_DIR + key + '/'  # 拼接关键字路径
        bv_list = os.listdir(key_path)  # 获取全部的bv路径
        if '.DS_Store' in bv_list:  # 删除mac系统自带的.DS_Store文件
            bv_list.remove('.DS_Store')
        for bv in bv_list:  # 遍历bv列表
            all_json.append(key_path + bv)  # 加入最终结果
    return all_json  # 返回全部bv路径


def clear_empty(raw_data: dict):
    for key in list(raw_data.keys()):  # 遍历所有的bv
        if not raw_data[key]:  # 判断弹幕是否为空
            raw_data.pop(key)  # 空则pop掉


def to_dataframe(raw_data: dict):
    result = pd.DataFrame([raw_data]).T
    result.columns = ['raw_danmu']
    return result


def stat(df: pd.DataFrame):
    df['num'] = df['raw_danmu'].apply(lambda x: len(x))
    df['length'] = df['raw_danmu'].apply(lambda x: sum(list(map(lambda y: len(y), x))))
    df['avg_length'] = df[['length', 'num']].apply(lambda row: row['length'] / row['num'], axis=1)
    print(df)


if __name__ == '__main__':
    all_data = dict()  # 准备bv号与弹幕的键值对
    files = get_all_json()  # 获取全部文件
    for file in files:  # 遍历文件
        all_data[get_bvid(file)] = formatted(file)  # 组装字典
    clear_empty(all_data)
    data = to_dataframe(all_data)
    # stat(data)
    # print(data)
