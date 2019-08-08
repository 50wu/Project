#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 26 10:16:03 2019

@author: nwu
"""
import sys
import time
from datetime import datetime, timedelta
import xlrd, xlwt
from xlutils.copy import copy
import collections
from deviceidentifier import api
import logging

logging.basicConfig()
logger = logging.getLogger('logger')
logger.warning('The system may break down')

class RefreshPC():
    '''
    The following code is going to get users whose laptop are over three years.
    '''
    def __init__(self, infile, outfile):
        self.infile = infile
        self.outfile = outfile
        
    def getFile(self, file):
        try:
            data = xlrd.open_workbook(file)
            return data
        except Exception as e:
            print (str(e))
        
    def readFile(self, file, by_index = 0):
        data = self.getFile(file)
        table = data.sheet_by_index(by_index)
        colnames = table.row_values(0)
        # get colomun item 'Serial Number' and 'Primary User' location
        index1 = colnames.index('Serial Number')
        index2 = colnames.index('Primary User')
        nrows = table.nrows
        result = []
        for rownum in range(1, nrows):
            row = table.row_values(rownum)
            if row:
                # make sure dictionary is ordered
                app = collections.OrderedDict()
                #get every row value of item 'Serial Number' and 'Primary User'
                app['Serial Number'] = row[index1]
                app['Primary user'] = row[index2]
                result.append(app)
        return result
        
    def lookUp(self, serial_number):
        info = api.lookup(api.TYPE_APPLE_SERIAL, serial_number)
        date = info['manufacturing']['date']
        year = timedelta(365)
        end_date = (datetime.strptime(date, '%Y-%m-%d') + 3 * year).strftime('%Y-%m-%d')
        return (date,end_date)

    def needRefresh(self, serial_number):
        end_date = self.lookUp(serial_number)[1]
        current_date = time.strftime("%Y-%m-%d", time.localtime())
        time_diff = (datetime.strptime(end_date, "%Y-%m-%d") - datetime.strptime(current_date, "%Y-%m-%d")).days
        # laptop over three years can be refreshed. You can requeset two month earlier.
        return time_diff <= 60
    
    def newFile(self):
        workbook = xlwt.Workbook(encoding = 'utf-8')
        worksheet = workbook.add_sheet('refresh_laptop')
        colume_name = ['Serial Number', 'Primary user', 'Manufacture Date', 'End of Life Date']
    
        row = 0
        for item in range(len(colume_name)):
            worksheet.write(row, item, colume_name[item])
        workbook.save(self.outfile)
    
        info = self.readFile(self.infile)
        for dic in info:
            serial_number = dic['Serial Number']
            if len(serial_number) == 11 or len(serial_number) == 12:
                if self.needRefresh(serial_number):
                    dic['Manufacture Date'] = self.lookUp(serial_number)[0]
                    dic['End of Life Date'] = self.lookUp(serial_number)[1]
                    # loop through each row and write a value to each column
                    row += 1
                    for item in range(len(dic)):
                        values = list(dic.values())
                        worksheet.write(row, item, values[item])
        workbook.save(self.outfile)
        
    def updateFile(self, by_index = 0):
        data = self.getFile(self.infile)
        dataCopy = copy(data)
        table = data.sheet_by_index(by_index)
        tableCopy = dataCopy.get_sheet(by_index)
        colnames = table.row_values(0)
        index1 = colnames.index('Serial Number')
        index2 = colnames.index('End of Life Date')
        nrows = table.nrows
        for rownum in range(1, nrows):
            row = table.row_values(rownum)
            end_date = self.lookUp(row[index1])[1]
            tableCopy.write(rownum, index2, end_date)
        dataCopy.save(self.infile)
        
    def process(self):
        self.newFile()
        self.updateFile()
        
        
  
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("invalid arguments")
        sys.exit(1)
        
    infile, outfile = sys.argv[1:]
    
    ref = RefreshPC(infile, outfile)
    ref.process()
