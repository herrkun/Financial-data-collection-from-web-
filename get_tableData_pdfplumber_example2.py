# -*- coding: utf-8 -*-
"""
Created on Sun Apr 21 03:06:40 2019

this just is a test file , a common extract file will be done later.
该文件可以获得pdf文件中的表格信息并返回，pdfplumber对表格的处理能力强于pdfminer

@author: herr_kun
"""



import pdfplumber
import re

path = r'C:\Users\herr_kun\Desktop/hello.pdf'

pdf = pdfplumber.open(path)

for page in pdf.pages:
    print(page.extract_text())
    for pdf_table in page.extract_tables():
        table = []
        cells = []
        for row in pdf_table:
            if not any(row):
                # 如果一行全为空，则视为一条记录结束
                if any(cells):
                    table.append(cells)
                    cells = []
            elif all(row):
                # 如果一行全不为空，则本条为新行，上一条结束
                if any(cells):
                    table.append(cells)
                    cells = []
                table.append(row)
            else:
                if len(cells) == 0:
                    cells = row
                else:
                    for i in range(len(row)):
                        if row[i] is not None:
                            cells[i] = row[i] if cells[i] is None else cells[i] + row[i]
        for row in table:
            print([re.sub('\s+', '', cell) if cell is not None else None for cell in row])
        print('---------- 分割线 ----------')

pdf.close()