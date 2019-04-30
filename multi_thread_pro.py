# -*- coding: utf-8 -*-
"""
Created on Fri Apr 26 15:40:31 2019

@author: Herr-kun
"""

from get_urlOfpdf_wyk import standardize_dir,__log_error,__filter_illegal_filename
from read_csv_stockids_wyk import parase_id
#from get_urlOfpdf_wyk import *
import csv
import os
import time
import math
import socket
import requests
from queue import Queue
import threading
import pdfplumber
import logging

rLock = threading.RLock() 
rLock2 = threading.RLock()
rLock3 = threading.RLock()

url_list=Queue()
pdffile_list=Queue()


OUTPUT_FILENAME = 'report'
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

def get_response(page_num,stack_code,return_total_count=False,START_DATE = '2013-01-01',END_DATE = '2018-01-01'):
    global url_list
    query = {
        'stock': stack_code,
        'searchkey': '',
        'plate': '',
        'category': CATEGORY,
        'trade': '',
        'column': '', #注意沪市为sse
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
    #reloading = 0
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
            if file_name.endswith('.PDF') or file_name.endswith('.pdf'):
                if '取消' not in file_name and '摘要' not in file_name and '年度' in file_name and\
                '更正' not in file_name and '英文' not in file_name and '补充' not in file_name:
                    result_list.append([file_name, file_link])
                    rLock.acquire() 
                    url_list.put([file_name, file_link])
                    rLock.release()
        return result_list

def get_url(OUT_DIR,stack_code_set,START_DATE,END_DATE): 
    START_DATE=START_DATE+'-01-01'
    END_DATE=END_DATE+'-01-01'
    # 初始化重要变量
    out_dir = standardize_dir(OUT_DIR)
    error_log = out_dir + 'error.log'
    output_csv_file = out_dir + OUTPUT_FILENAME.replace('/', '') + '_' + \
                      START_DATE.replace('-', '') + '-' + END_DATE.replace('-', '') + '.csv'
    #with open(output_csv_file, 'w', newline='', encoding='gb18030') as csv_out:
    csv_out=open(output_csv_file, 'w', newline='', encoding='gb18030')
    writer = csv.writer(csv_out)
    
    start=time.time()
    
    for stack_code in stack_code_set:
        # 获取记录数、页数
        item_count = get_response(1,stack_code,True,START_DATE = START_DATE,END_DATE = END_DATE)
        assert (item_count != []), 'Please restart this script!'
        begin_pg = 1
        end_pg = int(math.ceil(item_count / MAX_PAGESIZE))
        print('Page count: ' + str(end_pg) + '; item count: ' + str(item_count) + '.')
        time.sleep(2)
    
        # 逐页抓取
        #with open(output_csv_file, 'w', newline='', encoding='gb18030') as csv_out:
            #writer = csv.writer(csv_out)
        for i in range(begin_pg, end_pg + 1):
            row = get_response(i,stack_code,START_DATE = START_DATE,END_DATE = END_DATE)
            if not row:
                __log_error('Failed to fetch page #' + str(i) +
                            ': exceeding max reloading times (' + str(MAX_RELOAD_TIMES) + ').')
                continue
            else:
                writer.writerows(row)                
                last_item = i * MAX_PAGESIZE if i < end_pg else item_count
                print('Page ' + str(i) + '/' + str(end_pg) + ' fetched, it contains items: (' +
                      str(1 + (i - 1) * MAX_PAGESIZE) + '-' + str(last_item) + ')/' + str(item_count) + '.')
    csv_out.close()
    
    end=time.time()
    
    print('********time to open processing all files are {}*********'.format((end-start)))
    
    return output_csv_file

def download_pdf(path,MAX_COUNT = 5):
    global url_list
    global pdffile_list
    global logger
    print('get in download')
    print(url_list.qsize())
    DST_DIR=path
    assert (os.path.exists(DST_DIR)), 'No such destination directory \"' + DST_DIR + '\"!'
    if DST_DIR[len(DST_DIR) - 1] != '/':
        DST_DIR += '/'
    # 读取待下载文件列表
    print("run here")
    
    while True:
        rLock.acquire()            # 在此处加锁后，必须有对应的解锁，下面加一个else防止死锁
        if not url_list.empty():
            #rLock.acquire()
            each =url_list.get()
            print('get')
            rLock.release()
            download_count = 1
            download_token = False
            while download_count <= MAX_COUNT:
                try:
                    download_count += 1
                    r = requests.get(each[1])
                    download_token = True
                    break
                except:
                    # 下载失败则报错误
                    logger.error('Failed to download file', exc_info=True)
                    now_thread=threading.current_thread()             
                    logger.warning(now_thread.getName()+str(now_thread.isAlive()))
                    print(str(each[0] + 1) + '::' + str(download_count) + ':\"'  + '\" failed!')
                    download_token = False
                    time.sleep(3)       # 防止频繁访问网站被当做攻击关闭连接
            if download_token:
                # 下载成功则保存
                with open(DST_DIR + each[0], 'wb') as file:
                    file.write(r.content)
                    r.close()
                    time.sleep(3)
                    print(each[0] + '\" downloaded.')
                    rLock2.acquire()
                    pdffile_list.put(DST_DIR + each[0])
                    print('write pdf address ')
                    rLock2.release()
            else:
                # 彻底下载失败则记录日志
                with open(DST_DIR + 'error.log', 'a') as log_file:
                    log_file.write(
                        time.strftime('[%Y/%m/%d %H:%M:%S] ', time.localtime(time.time())) + 'Failed to download\"' +
                        each[0] + '\"\n')
                    print('...' + each[0] + '\" finally failed ...')
        else:
            rLock.release()


def parase_pdf(table_keyword,inside_keyword,outside_keyword):
    
    global pdffile_list
    global parase_out_writer
    global parase_out
    while True:
        try:
            rLock2.acquire()
            if not pdffile_list.empty():
                #rLock2.acquire()
                path =pdffile_list.get()
                print('get pdf address')
                rLock2.release()
                
                open_pdf_succeed=1
                start1=time.time()
                try:
                    pdf = pdfplumber.open(path,password='')
                except:
                    os.remove(path)    # 屏蔽此处的话，如果文件打开出错，则不会删除
                    open_pdf_succeed=0
                    print("*************open pdf error*******************")
                start2=time.time()
                if open_pdf_succeed:
                    print("*************open pdf succeed*******************")
                    find_table=0
                    find_pre_table=0
                    find_keyword=0
                    find_keyword_outside=0
                    name_find=[]
                    value_find=[]
                    page_find=[]
                    #for page in pdf.pages:
                        #print(page.extract_text())
                    begin_index=int(len(pdf.pages)/2)
                    for i in range(begin_index,len(pdf.pages)):  
                        if find_table:
                            find_pre_table=1
                        else:
                            find_pre_table=0
                        find_table=0
                        page=pdf.pages[i]
                        #print(page.extract_text())
                        data=page.extract_text()
                        if len(table_keyword):
                            for keyword in table_keyword:
                                if keyword in data:
                                    find_table=1
                                else:
                                    find_table=0
                                    break
                        else:
                            find_table=1
                
                        if find_table or find_pre_table:    
                            data_list=data.strip().split()
                            for j in range(len(data_list)):
                                if len(inside_keyword):
                                    for keyword in inside_keyword:
                                        if keyword in data_list[j]:
                                            find_keyword=1
                                else:
                                    find_keyword=1
                                    
                                if find_keyword:
                                    find_keyword=0
                                    print('run here')
                                    if len(outside_keyword):
                                        for keyword in outside_keyword:
                                            if keyword not in data_list[j]:
                                                find_keyword_outside=1
                                            else:
                                                find_keyword_outside=0
                                                break
                                    else:
                                        find_keyword_outside=1
                                        
                                    if find_keyword_outside:
                                        find_keyword_outside=0
                                        try:
                                            temp_value=data_list[j+1]
                                            temp_value=temp_value.replace(',','')
                                            temp_value=float(temp_value)
                                            name_find.append(data_list[j])
                                            value_find.append(temp_value)
                                            page_find.append(i)
                                            rLock3.acquire()
                                            try:
                                                parase_out_writer.writerows([[path.strip().split('/')[-1],data_list[j],str(temp_value),data_list[j+1],str(i)]]) 
                                            except:
                                                pass
                                            parase_out.flush()
                                            rLock3.release()
                                            print("*****find******{} value is {} and {}".format(data_list[j],data_list[j+1],temp_value))
                                            print("*************find in page {}*******************".format(i))
                                            print("*************find in {}*******************".format(path))
                                            break        # only find one result
                                        except:
                                            continue
                       
                    pdf.close()
                    start3=time.time()
                    
                    os.remove(path)    #  pdf.close 后删除文件 否则太多了
                    
                    print('****time to open PDF file is {}'.format((start2-start1)))
                    print('****time to processing PDF file is {}'.format((start3-start2)))
                
            else:
                rLock2.release()
                
        except:
            print('*****some thing error happend******')
            
    return name_find,value_find,page_find    # 一定不要把return放到while里面，遇到return会立即结束

def parase_saved():
    global parase_out_writer
    


OUT_DIR = r'D:/temp2'

socket.setdefaulttimeout(20)
logger = logging.getLogger()
logger.setLevel(logging.WARNING)  
rq = time.strftime('%Y%m%d%H%M', time.localtime(time.time()))
log_name = OUT_DIR + '/log_wyk.log'
logfile = log_name
fh = logging.FileHandler(logfile, mode='w')
fh.setLevel(logging.WARNING) 
formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
fh.setFormatter(formatter)
logger.addHandler(fh)


START_DATE = '2001'  
END_DATE = '2008'  #str(time.strftime('%Y-%m-%d')) 
table_keyword=['其他与经营活动','现金']
inside_keyword=['审计','咨询','中介']   # ,'咨询','中介'
outside_keyword=['收到']    


xlsfile = OUT_DIR+'/Audit Independence 1.xlsx'   # 打开指定路径中的xls文件
stack_code_set=parase_id(xlsfile)

#stack_code_set=['000004','000007']    # just for test using

parase_out_file_path=OUT_DIR+'/parase_out_file.csv'
parase_out=open(parase_out_file_path, 'w', newline='', encoding='gb18030')
parase_out_writer = csv.writer(parase_out)

get_url_thread = threading.Thread(target=get_url, args=(OUT_DIR,stack_code_set,START_DATE,END_DATE))
download_pdf_thread = threading.Thread(target=download_pdf, args=(OUT_DIR,))
#download_pdf_thread2 = threading.Thread(target=download_pdf, args=(OUT_DIR,))
parase_pdf_thread = threading.Thread(target=parase_pdf, args=(table_keyword,inside_keyword,outside_keyword))
parase_pdf_thread2 = threading.Thread(target=parase_pdf, args=(table_keyword,inside_keyword,outside_keyword))
parase_pdf_thread3 = threading.Thread(target=parase_pdf, args=(table_keyword,inside_keyword,outside_keyword))

get_url_thread.start()
download_pdf_thread.start()
#download_pdf_thread2.start()
parase_pdf_thread.start()
parase_pdf_thread2.start()
parase_pdf_thread3.start()

get_url_thread.join()
download_pdf_thread.join()
#download_pdf_thread2.join()
parase_pdf_thread.join()
parase_pdf_thread2.join()
parase_pdf_thread3.join()













