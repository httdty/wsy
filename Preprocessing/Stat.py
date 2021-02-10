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
UTILS_DIR = '../Utils/'
with open(UTILS_DIR + 'stopwords.txt', 'r') as file:
    STOP_WORDS = file.read().split()
STOP_WORDS = set(STOP_WORDS)
STOP_WORDS.add('')
STOP_WORDS.add(' ')
# with open(UTILS_DIR + 'userdict.txt', 'r') as f:
#     USER_DICT = set(f.read().split())
# jieba.load_userdict(USER_DICT)


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


# def to_word_list(raw_data: list):
#     doc = ' '.join(raw_data)
#     return jieba.lcut(doc)
#


def clean_word_list(raw_data: list):
    return list(filter(lambda y: y not in STOP_WORDS, raw_data))


def stat(df: pd.DataFrame):
    df['num'] = df['raw_danmu'].apply(lambda x: len(x))  # 弹幕数统计
    df['length'] = df['raw_danmu'].apply(lambda x: sum(list(map(lambda y: len(y), x))))  # 字数统计
    df['avg_length'] = df[['length', 'num']].apply(lambda row: row['length'] / row['num'], axis=1)  # 弹幕平均长度
    df['word_list'] = df['raw_danmu'].apply(lambda x: jieba.lcut(' '.join(x)))  # 切词
    df['word_list_len'] = df['word_list'].apply(lambda x: len(x))  # 获取词数
    df['word_num'] = df['word_list'].apply(lambda x: len(set(x)))  # 不重复词个数（词袋长度）
    df['clean_word'] = df['word_list'].apply(lambda x: list(filter(lambda y: y not in STOP_WORDS, x)))  # 去停用词
    df['clean_word_num'] = df['clean_word'].apply(lambda x: len(x))  # 统计词数


# 文本向量化
if __name__ == '__main__':
    all_data = dict()  # 准备bv号与弹幕的键值对
    files = get_all_json()  # 获取全部文件
    for file in files:  # 遍历文件
        all_data[get_bvid(file)] = formatted(file)  # 组装字典
    clear_empty(all_data)  # 清洗空数据
    data = to_dataframe(all_data)  # 转成dataframe类型
    stat(data)  # 生成统计
    # print(data)
