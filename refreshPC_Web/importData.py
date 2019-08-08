import sys
from pg import DB
import xlrd
import collections
from datetime import datetime, timedelta

class importData():

    def __init__(self, infile, table_name, dbname, host, port):
        self.infile = infile
        self.table_name = table_name
        self.dbname = dbname
        self.host = host
        self.port = port
    
    def getFile(self, file):
        try:
            data = xlrd.open_workbook(file)
            print(data)
            return data
        except Exception as e:
            print(str(e))
    
    def readFile(self, file, by_index = 0):
        data = self.getFile(file)
        table = data.sheet_by_index(by_index)
        colnames = table.row_values(0)
        # get colomun item 'Serial Number' and 'Primary User' location
        index1 = colnames.index('Serial Number')
        index2 = colnames.index('Primary User')
        index3 = colnames.index('Creation Date')
        nrows = table.nrows
        result = []
        for rownum in range(1, nrows):
            row = table.row_values(rownum)
            if row:
                # make sure dictionary is ordered
                app = collections.OrderedDict()
                #get every row value of item 'Serial Number' and 'Primary User'
                app['Serial Number'] = row[index1]
                app['Primary user'] = row[index2].replace(" ", "_")
                if row[index3]:
                    app['Creation Date'] = xlrd.xldate.xldate_as_datetime(row[index3], data.datemode)
                else:
                    app['Creation Date'] = None
                result.append(app)
        return result
    
    def setupConnection(self):
        try:
            db = DB(dbname=self.dbname, host=self.host, port=self.port)
            return db
        except Exception as e:
            print(str(e))
    
    def insertTable(self):
        db = self.setupConnection()
        data = self.readFile(self.infile)
        sql_create = "CREATE TABLE " + self.table_name + " (sn text, name text, date text);"
        db.query(sql_create)
        year = timedelta(365)
        for dic in data:
            serial_number = dic['Serial Number']
            primary_user = dic['Primary user']
            create_date = dic['Creation Date']
            if create_date is None:
                continue
            end_date = (create_date + 3 * year).strftime('%Y-%m-%d')
            db.insert(self.table_name, sn=serial_number, date=end_date)
        db.close()
    

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("invalid arguments")
        sys.exit(1)
        
    dbname = "gpadmin"
    host = "nwu"
    port = 15432
    table_name = "assets1"
    infile = sys.argv[1]
    imData = importData(infile, table_name, dbname, host, port)
    imData.insertTable()    












