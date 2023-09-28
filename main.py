import numpy as np
import pandas as pd
import requests
import os
from mysql.connector import connect , Error
import re
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

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
        self.host=os.getenv("HOST")
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
        
        
def testProcess(idStudio,tpst='otro', finicio ='' , ffin ='', nrecord=5):
    if tpst == 'otro':url =f'https://www.easysalespruebas.com.co/ServiciosEasySurvey/api/ObtenerExportadoEncuesta?usuario=EasySurveyClientMeiko&password=EasySurveyClientMeiko&id_encuesta={idStudio}&idr_encabezado=0'
    else: url= f'https://www.easysalespruebas.com.co/ServiciosEasySurvey/api/ObtenerExportadoEncuestaRangoFechaRecepcion?usuario=EasySurveyClientMeiko&password=EasySurveyClientMeiko&id_encuesta={idStudio}&fecha_inicial={finicio}000000&fecha_final={ffin}235959'
    req = requests.get(url)
    if req.status_code==200:
        
        #falta modulo de eliminacion archivos temporales estudios slecionados por nombre
        
        path=f'tmp/Studytest{idStudio}.csv'
        with open(path, 'wb') as file:
            file.write(req.content)
            file.close()
            
        with open(path, 'rb') as fileRead:
            line_count = sum(1 for line in fileRead)
            if line_count <=2 :
                return f'No hay registros #{line_count}' 
            else:
                data= pd.read_csv(path).tail(nrecord)
                data= data[['Auditor','Response.Received','Descripcion','responseModified','ENCUESTADOR','pre_nombreestablecimiento']]
                result=data.to_numpy()
                result=data.to_dict(orient='records')
                #f1=result.shape
                return result
    else: return f'Error en la consulta Estudio no encontrado  http:{req.status_code}'


def StudyModificator():
    FilePathBase=Path('db','BaseEstudios.csv')
    with open(FilePathBase, 'wb') as BaseWirtte:
        BaseWirtte.write()#terminar
        BaseWirtte.close()
    
    with open(FilePathBase, 'rb') as BaseRead:
        BaseRead.write()#terminar
        BaseRead.close()    
        