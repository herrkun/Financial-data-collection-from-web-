# -*- coding: utf-8 -*-
"""
Created on Sun Apr 21 01:42:51 2019
从网上获得的一个例子，可以取得某个特定的数据，该文件留作以后分析的例子使用
修改源文件：file_link = 'http://www.cninfo.com.cn/' + str(each['adjunctUrl']) 为
file_link = 'http://static.cninfo.com.cn/' + str(each['adjunctUrl'])
否则因为原网站更新升级了，无法打开原来的文件
@author: herr_kun
"""

# coding = utf-8

import csv
import math
import os
import time
import requests



START_DATE = '2018-07-16'  # 搜索的起始日期
END_DATE = str(time.strftime('%Y-%m-%d'))  # 默认当前提取，可设定为固定值
OUT_DIR = 'D:/XML/2018年年度报告'
OUTPUT_FILENAME = '2018年度报告'
# 板块类型：沪市：shmb；深市：szse；深主板：szmb；中小板：szzx；创业板：szcy；
PLATE = 'szzx;'
# 公告类型：category_scgkfx_szsh（首次公开发行及上市）、category_ndbg_szsh（年度报告）、category_bndbg_szsh（半年度报告）
CATEGORY = 'category_ndbg_szsh;'

URL = 'http://www.cninfo.com.cn/new/hisAnnouncement/query'
HEADER = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest'
}
MAX_PAGESIZE = 50
MAX_RELOAD_TIMES = 5
RESPONSE_TIMEOUT = 10


def standardize_dir(dir_str):
    assert (os.path.exists(dir_str)), 'Such directory \"' + str(dir_str) + '\" does not exists!'
    if dir_str[len(dir_str) - 1] != '/':
        return dir_str + '/'
    else:
        return dir_str


# 参数：页面id(每页条目个数由MAX_PAGESIZE控制)，是否返回总条目数(bool)
def get_response(page_num, return_total_count=False):
    query = {
        'stock': '',
        'searchkey': '',
        'plate': PLATE,
        'category': CATEGORY,
        'trade': '',
        'column': 'szse', #注意沪市为sse
#        'columnTitle': '历史公告查询',
        'pageNum': page_num,
        'pageSize': MAX_PAGESIZE,
        'tabName': 'fulltext',
        'sortName': '',
        'sortType': '',
        'limit': '',
        'showTitle': '',
        'seDate': START_DATE + '~' + END_DATE,
    }
    result_list = []
    reloading = 0
    while True:
#        reloading += 1
#        if reloading > MAX_RELOAD_TIMES:
#            return []
#        elif reloading > 1:
#            __sleeping(random.randint(5, 10))
#            print('... reloading: the ' + str(reloading) + ' round ...')
        try:
            r = requests.post(URL, query, HEADER, timeout=RESPONSE_TIMEOUT)
        except Exception as e:
            print(e)
            continue
        if r.status_code == requests.codes.ok and r.text != '':
            break
    my_query = r.json()
    try:
        r.close()
    except Exception as e:
        print(e)
    if return_total_count:
        return my_query['totalRecordNum']
    else:
        for each in my_query['announcements']:
            file_link = 'http://static.cninfo.com.cn/' + str(each['adjunctUrl'])
            file_name = __filter_illegal_filename(
                str(each['secCode']) + str(each['secName']) + str(each['announcementTitle']) + '.'  + '(' + str(each['adjunctSize'])  + 'k)' +
                file_link[-file_link[::-1].find('.') - 1:]  # 最后一项是获取文件类型后缀名
            )
            result_list.append([file_name, file_link])
        return result_list


def __log_error(err_msg):
    err_msg = str(err_msg)
    print(err_msg)
    with open(error_log, 'a', encoding='gb18030') as err_writer:
        err_writer.write(err_msg + '\n')


def __filter_illegal_filename(filename):
    illegal_char = {
        ' ': '',
        '*': '',
        '/': '-',
        '\\': '-',
        ':': '-',
        '?': '-',
        '"': '',
        '<': '',
        '>': '',
        '|': '',
        '－': '-',
        '—': '-',
        '（': '(',
        '）': ')',
        'Ａ': 'A',
        'Ｂ': 'B',
        'Ｈ': 'H',
        '，': ',',
        '。': '.',
        '：': '-',
        '！': '_',
        '？': '-',
        '“': '"',
        '”': '"',
        '‘': '',
        '’': ''
    }
    for item in illegal_char.items():
        filename = filename.replace(item[0], item[1])
    return filename


if __name__ == '__main__':
    # 初始化重要变量
    out_dir = standardize_dir(OUT_DIR)
    error_log = out_dir + 'error.log'
    output_csv_file = out_dir + OUTPUT_FILENAME.replace('/', '') + '_' + \
                      START_DATE.replace('-', '') + '-' + END_DATE.replace('-', '') + '.csv'
    # 获取记录数、页数
    item_count = get_response(1, True)
    assert (item_count != []), 'Please restart this script!'
    begin_pg = 1
    end_pg = int(math.ceil(item_count / MAX_PAGESIZE))
    print('Page count: ' + str(end_pg) + '; item count: ' + str(item_count) + '.')
    time.sleep(2)

    # 逐页抓取
    with open(output_csv_file, 'w', newline='', encoding='gb18030') as csv_out:
        writer = csv.writer(csv_out)
        for i in range(begin_pg, end_pg + 1):
            row = get_response(i)
            if not row:
                __log_error('Failed to fetch page #' + str(i) +
                            ': exceeding max reloading times (' + str(MAX_RELOAD_TIMES) + ').')
                continue
            else:
                writer.writerows(row)                
                last_item = i * MAX_PAGESIZE if i < end_pg else item_count
                print('Page ' + str(i) + '/' + str(end_pg) + ' fetched, it contains items: (' +
                      str(1 + (i - 1) * MAX_PAGESIZE) + '-' + str(last_item) + ')/' + str(item_count) + '.')

