import numpy as np
import pandas as pd
import requests
import os
from mysql.connector import connect , Error


class DataProcess():
    def __init__(self, data_path,extFile):
        self.extFile=extFile
        self.filePath=data_path
        if(self.extFile=='xlsx'): self.csvFile = pd.read_excel(self.filePath)   
        else: self.csvFile = pd.read_csv(self.filePath)
    
    def _dataProcessHeaders(self):
        return self.csvFile.columns
        #data1=csvFile.loc[csvFile['CodifoclienteKof_Mex'].notna()==False,['idEstablecimiento','FotoStickerFemsa','CodifoclienteKof_Mex']].head(5) #obtenenemos las filas que no tienen Codigo Aun

    def _dataProcessHead(self):
        file=self.csvFile.tail(5)
        file.to_numpy()
        f1=file.shape
        return f1
    
class DB():
    def __init__(self, dbName=''):
        self.host='meiko-prod.cmebrzxfmsvx.us-east-2.rds.amazonaws.com'
        self.user='support_data'
        self.password='puHnBWtMOzQzHarQMhnmhooy'
        self.port=3306
        self.dbName= dbName 
        self.config = {
                'user': self.user,
                'password': self.password,
                'host': self.host,
                'database': self.dbName,
                'port':self.port,
                'raise_on_warnings': True
        }
        
    def _newQuerySelect(self, query,responseType=''):
        #query="SELECT * FROM jobOrder.sp_mega_job_nf WHERE anio = 2023 LIMIT 10"
        conn=connect(**self.config)
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query)
            result=cursor.fetchall()
        except Error as e:
            return f'An Error ocurred {e}'
        cursor.close() 
        conn.close
        return result    
        
        




