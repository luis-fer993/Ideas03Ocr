from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
from main import DataProcess, DB
from mysql.connector import connect , Error


app=Flask(__name__)

@app.route('/')
def index():
    options={
        'PageName':'File Upload',
        'typeProcess':'login'
        }
    return render_template('index.html',**options)


@app.route('/upload', methods=['POST','GET'])
def upload_file():
    if request.method == 'POST':
        f = request.files['file']
        extFile=str(f.filename.split('.')[-1])
        if f.filename =='' or  extFile not in ['xlsx', 'csv', 'txt']:
            return '404',404
        
        filePath=f'tmp/{secure_filename(f.filename)}'
        f.save(filePath)
        FileStaus="The file is saved as %s "%filePath
        File= DataProcess(filePath,extFile)
        #varibles
        data = FileStaus
        PageName = "Data Process"
        ctx ={
            'data':data,
            'PageName':PageName,
            'typeProcess':'dataViwer',
            'processResult':File._dataProcessHeaders(),
            'fileHeaders':File._dataProcessHead(),
            'conn': File
        }
        return render_template('index.html',**ctx)
    else: return '404',404


@app.route('/process')
def process():
    conn= DB('jobOrder')
    query="SELECT * FROM sp_mega_job_nf WHERE anio = 2023 LIMIT 10"
    try:
        connection=connect(**conn.config)
        cursor = connection.cursor()
        result=cursor.execute(query)
    except Error as e:
        return f'An Error ocurred {e}'
    ctx={
        'result':result
    }
    cursor.close() 
    connection.close()
    return render_template('process.html',**ctx)
    
    

    




