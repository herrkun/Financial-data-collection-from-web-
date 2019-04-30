# Financial-data-collection-from-web-
A python scripe that collecting financial data from ju-chao web, and can download pdf files from it , more important is it can parase data you want from pdf files using pdfplumber .

### platform:  
### win10 anaconda python3.7 pdfplumber==0.5.12     
### (Don't install pdfminer if you have installed pdfplumber,it will destroy the envoronment as pdfplumber used a another version of pdfminer as backend)

* *original_data dir*: test files prepared for test,you can use them by modify the file path in .py files

* download_files dir: download dir saving download files from the web

* output_files dir: a dir of output files, you can find files here which were created in .py files

* download_filesFromcsv_wyk.py can download files from the web according the url-link in .csv files, the  url-link is just like:  
000002万科A2012年年度报告.(1848k).PDF	http://static.cninfo.com.cn/finalpage/2013-02-28/62162993.PDF

* get_urlOfpdf_wyk.py is a formal scrip that for getting pdf_url_link from Ju-Chao website,and it creats a csv file which saving url-link like:   
eg:600486扬农化工2013年年度报告.(3507k).PDF	http://static.cninfo.com.cn/finalpage/2014-03-18/63689220.PDF  
600486扬农化工2012年年度报告.(3442k).PDF	http://static.cninfo.com.cn/finalpage/2013-03-29/62295434.PDF  
000049德赛电池2016年年度报告.(4218k).PDF	http://static.cninfo.com.cn/finalpage/2017-03-13/1203150233.PDF  
000049德赛电池2015年年度报告(更新后).(4080k).PDF	http://static.cninfo.com.cn/finalpage/2016-03-29/1202089761.PDF  
000049德赛电池2014年年度报告.(3976k).PDF	http://static.cninfo.com.cn/finalpage/2015-03-03/1200662592.PDF  

* multi_thread_pro.py is a multi threads project, which can get the url,download pdf files and parase files at the same time,for using this project you just need to modify "OUT_DIR" "START_DATE" .... such parameters to your owns.  
START_DATE = '2001'  END_DATE = '2008'  #str(time.strftime('%Y-%m-%d')) are parameters to limit the year of annual report,  
table_keyword=['其他与经营活动','现金'] is the flag of the data you want ,it means you want '其他与经营活动' and '现金' appears, and you can change the keywords and the count of keywords,it can also be ['其他与经营活动','现金','支付','xxxx']   
inside_keyword=['审计','咨询','中介']  are keywords you want to appear in the sentence, it means you want '审计'or '咨询' or '中介'appears.(here is 'or'  not 'and',one of these keywords appears is ok)  
outside_keyword=['收到']  are keywords you don't want to appear in a sentence, it means you don't want '收到' and other keywords appears.  

* parase_data_pdfplumber_wyk.py is a scrip for analyse a signal pdf file,you just need to modify the pdf file path to yours for using , and if pdf file have the infomation you want ,it will print message on the console just like:   
" *************find*******************咨询及审计费 value is 1,252,388 "
" *************find in page*******************75 "  

* read_csv_stockids_wyk.py is a scrip for parasing stock_id from a csv files.you can save a excel file copy to a csv file. and it returns a set of stock ids which having no repeating elements.  

* singal_parase_data_from_download.py is a file that for parasing pdf files as your pdf files are under a dir,it can find out all pdf files undering the dir,and parasing them one by one.  

some testing files:  
process_all.py import other scrips as a model,and you can use them having a simple processing stream.  
parase_data_pdfminer_example.py is a example of using pdfminer model not pdfplumber to making a analyse.  
del_test.py is just a test file that you can ignore,and can also be a test files for testing some function  
get_tableData_pdfplumber_example.py and get_tableData_pdfplumber_example2.py are examples showing the skills using pdfplumber,you can have a preview before running.   
get_url_example.py is also a example that for testing ideas.  
parase_data_from_download.py also is a testing file can be ignore  


#### Debug experience:
* using try except to avoid exceptions, some exceptions may happen when opening pdf files,use try-except struct to ignore them,and turn to the next  
* if you are downloading many pdf files, suggesting to use os.remove() after parasering files  
* their may be a error when accessing the ju chao web for downloading many pdf files, because the ju chao web think you as a web-attack as accessing frequently. use time.sleep or try except to solve this problem.  error: ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接  

to be continued......
