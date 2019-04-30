# -*- coding: utf-8 -*-
"""
Created on Sun Apr 21 10:22:45 2019
读取并获得数据Excel中所有的股票ID
@author: herr_kun
"""

import xlrd

def parase_id(path):
    stack_code_set=[]
    if path.endswith('.xlsx') or path.endswith('.xls'):
        try:
            book = xlrd.open_workbook(path)      #得到Excel文件的book对象，实例化对象
            sheet0 = book.sheet_by_index(0)         # 通过sheet索引获得sheet对象
            sheet_name = book.sheet_names()[0]     # 获得指定索引的sheet表名字
            print (sheet_name)
            #sheet1 = book.sheet_by_name(sheet_name)    # 对于多个sheet可以这样使用
            
            nrows = sheet0.nrows    # 获取行总数
            ncols = sheet0.ncols    # 获取列总数
            print ('the number of rows and cols are : ',nrows,ncols)
            
            for i in range(nrows):
                data=sheet0.cell_value(i, 0)
                try:
                    data_number=int(data)
                    stack_code_set.append(data)
                except:
                    continue
        except:
            stack_code_set=[]
            
    if path.endswith('.txt'):
        try:
            file=open(path,'r')
            for line in file.readlines():
                stack_code_set.extend(line.strip().split())
        except:
           pass
    else:
        path=path.strip()
        try:
            data_number=int(path)
            stack_code_set.append(path)
        except:
            pass
    
    stack_code_set=set(stack_code_set)
    return stack_code_set


if __name__=='__main__':
    xlsfile = r"C:\Users\herr_kun\Desktop\Audit Independence 1.xlsx"    # 打开指定路径中的xls文件
    stack_code_set=parase_id(xlsfile)