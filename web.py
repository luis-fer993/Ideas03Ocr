from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
from main import DataProcess, DB
conn= DB()

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
            'fileHead':File._dataProcessHead(),
            'conn': File
        }
        return render_template('index.html',**ctx)
    else: return '404',404


@app.route('/process',methods=['POST','GET'])
def process():
    if request.method=='POST':
        for column in request.form:
            pass
        query="SELECT * FROM jobOrder.sp_mega_job_nf WHERE anio = 2023 LIMIT 10"
        ctx={
            'result':conn._newQuerySelect(query)
            #'req':data
        }
        return render_template('process.html',**ctx)
    else:
        return '404', 404
    
@app.route('/hashcompare')
def hashcompare():
    ctxhash={}
    ctxhash['countries']='''select * from geomaster.paises'''
    ctxhash['cycles']='''select * from jobOrder.ciclos'''
    ctxhash['studies']='''select * from jobOrder.estudios'''
    ctxhash['clients']='''select * from jobOrder.clientes '''
    #ctxhash['meditionTypes']='''SELECT	DISTINCT tipos_medicion FROM jobOrder.sp_mega_job_nf'''

    for val in (ctxhash.keys()):
        v1=ctxhash[val]
        ctxhash[val]=conn._newQuerySelect(v1)
    return render_template('hash.html',**ctxhash)
    

    




