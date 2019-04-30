# -*- coding: utf-8 -*-
"""
Created on Sun Apr 21 03:16:22 2019
因为PDF中的表格有的是封闭式的，有的是开放式的，对开放式的表格的处理不是很准确，识别不出来是table
所以就进不去table的判断，因此最终使用直接解析text数据的方式，也就是untiled 6 文件
@author: herr_kun
"""




import pdfplumber
import re

path1 = r'C:\Users\herr_kun\Desktop/63889879.pdf'    # 97
path2 = r'C:\Users\herr_kun\Desktop/东阿阿胶：2017年年度报告（更新后）.pdf'   #124
pdf = pdfplumber.open(path2)
find_table=0
find_pre_table=0
#for page in pdf.pages:
    #print(page.extract_text())
#for i in range(int(len(pdf.pages)/2),len(pdf.pages)):  
if 1:
    if find_table:
        find_pre_table=1
    else:
        find_pre_table=0
    find_table=0
    page=pdf.pages[124]
    #print(page.extract_text())
    data=page.extract_text()
    if '经营活动' in data or '税金' in data:    # 判断界面中是否含有关键词，接下来才是表格
        find_table=1

    if find_table or find_pre_table:    
        #print('--------------- 分割线 ---------------')
        for pdf_table in page.extract_tables():
            print(pdf_table)
            table = []
            cells = []
            for row in pdf_table:
                #print('rows: {}' .format(row))
                #print('cells: {}' .format(cells))
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
                if '审计' in row or '咨询' in row or '管理' in row:
                    print("*************find*******************{}".format(row))
                    print("*************find page*******************{}".format(i))
                    print("*************find*******************")
            #print('--------------- 分割线 ---------------')

pdf.close()





a=[['项目', '本年发生额', '上年发生额'],['城市维护建设税', '32,903,002.88', '26,755,857.63'],['其他', '998,057.39', '614,181.97']]






