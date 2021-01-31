# -*- coding: utf-8 -*-
# @Time    : 2020/11/28 18:30
# @Author  : Ray
# @Email   : httdty2@163.com
# @File    : BiliBili.py
# @Software: PyCharm

import requests  # 负责发送网络请求
from bs4 import BeautifulSoup  # 解析HTML
import json  # 解析json
import time  # 时间控制
import random  # 引入随机数
import os  # 引入系统库

SEARCH_URL_TEMPLATE = [
    'https://search.bilibili.com/all?keyword=',
    '&from_source=nav_suggest_new&order=dm&duration=0&tids_1=0&page='
]  # URL的模板，后面与关键字组成URL

HEADERS = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_0_1) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36'
}  # 混淆视听，伪装成一个正常的浏览器

COOKIES = {
    'SESSDATA': '13d1f356%2C1627643093%2C3df13%2A11'
}  # 伪造cookies，完成登录

SEARCH_KEYWORD_LIST = ['高一语文', '高一数学', '高一英语']
PAGE = 1

MIN_CHAPTER_NUM = 5

# search_keyword = '高中数学'  # 搜索关键字
# page_num = 1  # 页码


def get_course_list(keyword, pages=5):
    course_dict = dict()  # 空字典course_dict，用来存储最终bv号和视频名称
    for page_num in range(pages):  # 多页抓取
        page_num += 1
        url = SEARCH_URL_TEMPLATE[0] + keyword + SEARCH_URL_TEMPLATE[1] + str(page_num)  # 利用URL的模板拼接成一个url
        r = requests.get(url=url, headers=HEADERS)  # 发起url请求
        soup = BeautifulSoup(r.text, 'html.parser')  # 解析html
        ul = soup.find('ul', class_='video-list clearfix')  # 找到ul标签
        li_list = ul.find_all('li')  # 找到所有的li标签
        for li in li_list:  # 遍历li列表
            a = li.find('a')  # 找到a标签
            bv = a['href'].split('/')[-1]  # 截取bv号
            bv = bv.split('?')[0]  # 获取完整bv号
            if len(bv) > 10:  # 对bv号进行基本检查，鲁棒性Robust
                course_dict[bv] = a['title']  # 获得url的list
    return course_dict  # 返回最终结果url的列表


def get_chapter_list(bv):
    chapter_query_url_template = ['https://api.bilibili.com/x/player/pagelist?bvid=',
                                  '&jsonp=jsonp']  # 章节id查询url模板
    url = chapter_query_url_template[0] + bv + chapter_query_url_template[1]  # 章节查询url拼接
    r = requests.get(url, headers=HEADERS)  # 发起所有请求
    raw_data = json.loads(r.text)  # 解析请求结果为字典
    raw_data = raw_data.get('data', [])  # 获取其中的data部分
    res_data = dict()  # 准备结果变量
    for d in raw_data:  # 遍历所有的章节
        res_data[d['cid']] = d['part']  # 加入结果字典中
    if len(res_data) < MIN_CHAPTER_NUM:  # 章节数量太少
        res_data = {}  # 去除不是系统性的课程
    return res_data  # 返回存放所有章节id和章节名称的字典


def get_danmu_chapter(chapter_id):
    print("开始处理：{}".format(chapter_id))
    date_query_url_template = ['https://api.bilibili.com/x/v2/dm/history/index?type=1&oid=',
                               '&month=2020-']  # 准备url模板
    result = dict()
    danmu_date_list = list()
    for month in range(12, 0, -1):  # 倒叙遍历月份
        url = date_query_url_template[0] + str(chapter_id) + date_query_url_template[1] + str(month)  # 组装URL
        r = requests.get(url, headers=HEADERS, cookies=COOKIES)  # 发起请求（伪装登录）
        print("正在获取 {} 月的日期列表\r".format(month), end='')
        time.sleep(random.randint(2, 5))  # 暂停
        raw_data = json.loads(r.text)  # 解析json文件
        raw_data = raw_data.get("data", [])  # 获取data
        if not raw_data:  # 无时间更久的弹幕出现
            break  # 退出循环
        danmu_date_list.extend(raw_data)  # 结果汇总
    total = len(danmu_date_list)  # 获取总长度
    current = 0  # 当前正在处理的日期位次
    for date in danmu_date_list:  # 遍历时间列表
        current += 1  # 位次+1
        print("正在处理：{}/{}\r".format(current, total), end='')  # 输出处理量
        result[date] = get_danmu(chapter_id, date)  # 获取弹幕
    print("处理完成：{}\r".format(chapter_id), end='')  # 完成处理提示
    return result  # 返回最终结果


def get_danmu(chapter_id, date):
    result = list()  # 准备结果
    # query 查询
    danmu_query_template = ['https://api.bilibili.com/x/v2/dm/web/history/seg.so?type=1&oid=',
                            '&date=']  # 弹幕查询url模板
    url = danmu_query_template[0] + str(chapter_id) + danmu_query_template[1] + str(date)  # 拼接url
    r = requests.get(url, headers=HEADERS, cookies=COOKIES)  # 发起请求
    if len(r.text) < 100 and "请求过于频繁，请稍后再试" in r.text:  # 封号处理
        print("请求过于频繁，请稍后再试")
        input("等待处理...")  # 操作请求
    time.sleep(random.randint(6, 8))  # 降低访问频率
    hos = ':'  # head of the sentence
    eos = '@'  # end of the sentence
    raw_data = r.text.split(eos)  # 切分弹幕
    for rd in raw_data:  # 遍历弹幕
        head = rd.find(hos)  # 找:
        if head > 0:  # 有效性判定
            # result.append(rd[head + 2:])  # 激进策略
            result.append(rd.split(':')[-1][1:])  # 弹幕数据添加
    return result  # 返回结果


def danmu_save(result, save_path):
    if result['data']:  # 结果判断
        f = open(save_path, 'w')  # 创建文件
        json.dump(result, f, ensure_ascii=False, indent="  ")  # 存储弹幕
        f.close()  # 关闭文件
        print("保存成功：" + save_path)  # 提示保存成功
    else:
        print("保存失败：" + save_path + "，非课程视频")  # 保存失败
    print('')  # 换行


if __name__ == '__main__':
    # search_keyword = '高一语文'
    for search_keyword in SEARCH_KEYWORD_LIST:
        print('-' * 30 + search_keyword + '-' * 30)  # 提示在处理的关键字
        dir_path = "../Data/" + search_keyword + '/'  # 组装文件夹路径
        if not os.path.exists(dir_path):  # 文件夹存在性判定
            os.mkdir(path=dir_path)  # 创建文件夹
        res = dict()  # 保存结果
        bvs = get_course_list(search_keyword, pages=PAGE)  # 获取所有的bv
        for bvid in bvs.keys():  # 遍历bv
            print("BV号：{}\t名称：{}".format(bvid, bvs[bvid]))  # 进度提示
            res[bvid] = {}  # 创建空字典
            res[bvid]['name'] = bvs[bvid]  # 设置名称
            res[bvid]['data'] = {}  # 创建data空字典
            chapter_dict = get_chapter_list(bvid)  # 获取全部chapter
            for cid in chapter_dict.keys():  # 比那里chapter_id
                res[bvid]['data'].update(get_danmu_chapter(cid))  # 获取该chapter的所有弹幕
            danmu_save(result=res[bvid], save_path=dir_path + str(bvid) + ".json")  # 保存单独bv结果
        danmu_save(result=res, save_path=dir_path + "all.json")  # 保存全部bv结果
