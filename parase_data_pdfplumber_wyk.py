# -*- coding: utf-8 -*-
"""
Created on Sun Apr 21 14:00:23 2019
处理单个文件的程序，看写的查找审计value是否可以正常使用，作为测试使用。

因为PDF中的表格有的是封闭式的，有的是开放式的，对开放式的表格的处理不是很准确，识别不出来是table
所以就进不去table的判断，因此最终使用直接解析text数据的方式，也就是untiled 6 文件

输出结果eg:
run here
*************find*******************咨询及审计费 value is 1,252,388
*************find in page*******************75
*************find*******************
****time to open PDF file is 0.5510315895080566
****time to processing PDF file is 8.935511112213135

@author: herr_kun
"""


import pdfplumber
import re
import time


def parase_pdf(path,table_keyword,inside_keyword,outside_keyword):
    start1=time.time()
    
    pdf = pdfplumber.open(path,password='')
    start2=time.time()
    
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
                        name_find.append(data_list[j])
                        value_find.append(data_list[j+1])
                        page_find.append(i)
                        print("*************find*******************{} value is {}".format(data_list[j],data_list[j+1]))
                        print("*************find in page*******************{}".format(i))
                        print("*************find*******************")
       
    pdf.close()
    start3=time.time()
    
    print('****time to open PDF file is {}'.format((start2-start1)))
    print('****time to processing PDF file is {}'.format((start3-start2)))
    
    return name_find,value_find,page_find



if __name__=='__main__':
    path1 = r'C:\Users\herr_kun\Pictures/深赤湾Ａ：深赤湾Ａ2003年年度报告.pdf'    # 71
    path2 = r'C:\Users\herr_kun\Desktop/东阿阿胶：2017年年度报告（更新后）.pdf'   #124

    table_keyword=['经营活动','现金']
    inside_keyword=['审计','咨询','中介']   # ,'咨询','中介'
    outside_keyword=['收到']
    a,b,c=parase_pdf(path1,table_keyword,inside_keyword,outside_keyword)   # return list





