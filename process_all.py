# -*- coding: utf-8 -*-
"""
Created on Thu Apr 25 22:12:37 2019

@author: herr_kun
"""

from read_csv_stockids_wyk import parase_id
from parase_data_pdfplumber_wyk import parase_pdf
from get_urlOfpdf_wyk import get_url
from download_filesFromcsv_wyk import download_pdf





# 从文件中获得 ID信息
#xlsfile = r"C:\Users\herr_kun\Desktop\Audit Independence 1.xlsx"    # 打开指定路径中的xls文件
#stack_code_set=parase_id(xlsfile)

# 从 ID信息 获得所需要的URL地址
START_DATE = '2002'  
END_DATE = '2007'  #str(time.strftime('%Y-%m-%d')) 
OUT_DIR = r'D:\temp'
    
stack_code_set=['000002','000004','000006','000007']
output_csv_file_path=get_url(OUT_DIR,stack_code_set,START_DATE,END_DATE)   # no returns

#download_pdf(output_csv_file_path)