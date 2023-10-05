import numpy as np
import pandas as pd
import requests
import os
from mysql.connector import connect , Error
import re
from pathlib import Path
import sqlite3
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
        
        
def testProcess(idStudio,tpst='otro', finicio ='' , ffin ='', nrecord=30):
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
                #result=data.to_html(classes='table table-striped tablacss')
                #f1=result.shape
                #result=data.to_html(classes='table table-dark')
                return result
    else: return f'Error en la consulta Estudio no encontrado  http:{req.status_code}'


def baseStudiesOperations(operation='r',data={}, raw=False,rd=None):
    #defult read file and data (r)
    #writte with (w)
    # path db/base.csv
    FilePathBase=Path('db','BaseEstudios.csv')
    if operation == 'w' and rd != None:
        with open(FilePathBase, 'wt', encoding='utf-8') as BaseWirtte:
            BaseWirtte.write(rd)#terminar
            BaseWirtte.close()
            
        return 'completado exitosamente'
            
            
    if operation == 'w':
        
        newEdit=pd.read_csv(FilePathBase)
        idEspecifico=newEdit.loc[newEdit['idtabla']==data['idtabla']]
        
        #newEdit.loc[int(idEspecifico.index[0]),'descripcion']='new9'

        for val in  idEspecifico.keys():
            newEdit.loc[int(idEspecifico.index[0]),val]=data[val]
        newEdit.to_csv(FilePathBase,index=False)
        
        result='Completado Exitosamente'
        
    else:
        BaseRead = pd.read_csv(FilePathBase)
        result = BaseRead.to_dict(orient='records')
        if raw != False:
            with open(FilePathBase, 'rt',encoding='utf-8') as BaseR:
                result=BaseR.read()#terminar
                BaseR.close() 
            
    return result
        
def baseQuery():
    FilePathBase=Path('db','BaseEstudios.db')
    conn = sqlite3.connect(FilePathBase)
    cursor = conn.cursor()
    # Define the SQL statement to create a table
    create_table_sql = '''
    CREATE TABLE IF NOT EXISTS easyestudios (
        idtabla INTEGER PRIMARY KEY,
        estudio TEXT,
        descripcion TEXT,
        idestudio INTEGER
    );
    '''
    query="""
    SELECT * FROM easyestudios
    """
    cursor.execute(query)
    data=cursor.fetchall()
    conn.commit()
    conn.close()
    return data
    