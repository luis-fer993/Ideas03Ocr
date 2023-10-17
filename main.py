import numpy as np
import pandas as pd
import requests
import os
from mysql.connector import connect , Error
import re
from pathlib import Path
import sqlite3
#from dotenv import load_dotenv
#load_dotenv()

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
        file.to_dict()
        f1=file.shape
        return f1
    
class DB():
    def __init__(self, dbName=''):
        self.host=os.getenv("HOST")
        self.user=os.getenv('USERDB')
        self.password=os.getenv('PASSWORDBB')
        self.port=os.getenv('PORT')
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
        
        
def testProcess(idStudio,tpst='pruebas', finicio ='' , ffin ='', nrecord=30):
    url,req, result ={},{},{}
    url['pruebas'] =f'https://www.easysalespruebas.com.co/ServiciosEasySurvey/api/ObtenerExportadoEncuesta?usuario=EasySurveyClientMeiko&password=EasySurveyClientMeiko&id_encuesta={idStudio}&idr_encabezado=0'
    url['produccion']= f'https://www.easysalespruebas.com.co/ServiciosEasySurvey/api/ObtenerExportadoEncuestaRangoFechaRecepcion?usuario=EasySurveyClientMeiko&password=EasySurveyClientMeiko&id_encuesta={idStudio}&fecha_inicial={finicio}000000&fecha_final={ffin}235959'
    if tpst == 'pruebas':
        req['pruebas'] = requests.get(url['pruebas'])
    elif tpst == 'produccion':
        req['produccion'] = requests.get(url['produccion'])
    elif tpst == 'ambos':
        for key, value in url.items():
            req[key]=requests.get(value) # save the result in adict with each key on each environment
        
        #req={'pruebas':reqestMethods,
        #     'produccion':reqestMethods}
        
    for k in req.keys(): # get the name of environment
        path=Path('tmp',f'Studytest{idStudio}_{k}.csv') # set the name of file
        
        listFile=os.listdir(path=Path('tmp')) #removing temporal files 
        matching_files = [filename for filename in listFile if re.match(f'Studytest_*', filename)]
        for i in range(0,len(matching_files)):
            if os.path.exists(path=Path('tmp',matching_files[i])):
                os.remove(Path('tmp',matching_files[i]))
                
        if req[k].status_code==200: #access to methods of each environmet
            #falta modulo de eliminacion archivos temporales estudios slecionados por nombre
            with open(path, 'wb') as file:
                file.write(req[k].content) #writte the content
                file.close()

            with open(path, 'rb') as fileRead:
                line_count = sum(1 for line in fileRead)
                if line_count <=2 : #if there is no record 
                    result[k] =[{'Informacion':f'No hay registros #{line_count}'} ]
                else:
                    data= pd.read_csv(path).tail(nrecord)#get the dataframe with numbers of rows
                    data= data[['Auditor','Response.Received','Descripcion','responseModified','ENCUESTADOR','pre_nombreestablecimiento']]
                    #setting headers 
                    result[k]=data.to_dict(orient='records') #saving information
        else: result[k]= [{'Informacion':f'Error en la consulta Estudio no encontrado  http:{k} : {req[k].status_code} '} ]
    return result


def baseStudiesOperations(operation='r',data={}, raw=False,rd=None):
    #defult read file and data (r)
    #data is a dict with the inputs values 
    #raw if we want get the raw file 
    #rd if we want to writte raw data 
    #writte with (w)
    #n new entry
    # path db/base.csv
    FilePathBase=Path('db','BaseEstudios.csv')
    if operation == 'w' and rd != None: #Writte file when a raw data is recived from form
        with open(FilePathBase, 'wt', encoding='utf-8') as BaseWirtte:
            BaseWirtte.write(rd)#terminar
            BaseWirtte.close()
        return 'completado exitosamente'    
            
    if operation == 'w': #writte when the data is recived from inputs forms
        newEdit=pd.read_csv(FilePathBase) #read the file 
        idEspecifico=newEdit.loc[newEdit['idtabla']==data['idtabla']] #get the row with the specific idtable
        
        if data['eliminar']=='on': 
            newEdit=newEdit[newEdit['idtabla'] != int(idEspecifico['idtabla'].values[0])] #remove row on idtable value
        else:     
            for val in  idEspecifico.keys():
                newEdit.loc[int(idEspecifico.index[0]),val]=data[val] # put each value on specific row 
        newEdit.to_csv(FilePathBase,index=False) #save the new file 
        
        result='Completado Exitosamente' 
        
    elif operation == 'n':
        newEntry={}
        for k, v in data.items(): #create the dict 
            newEntry[str(k)]=[v]
        df=pd.DataFrame(newEntry) #Create a new df, based on a dict 
        df.to_csv(FilePathBase,mode='a', index=False, header=False) #overwritte with the new information 
        
        result='Completado Exitosamente'   
        
    else: #just read file csv 
        BaseRead = pd.read_csv(FilePathBase)
        result = BaseRead.to_dict(orient='records') #if we want to get the DataFrame 
        if raw != False: #if we want to get the raw file data
            with open(FilePathBase, 'rt',encoding='utf-8') as BaseR:
                result=BaseR.read()#terminar
                BaseR.close() 
            
    return result #return result depend on


######### Test on Mysqli3 Base Local non implemented        
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
    