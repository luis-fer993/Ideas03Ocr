from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
from main import DataProcess, DB, testProcess, baseStudiesOperations, baseQuery
import pandas as pd
conn= DB()

#import flask

app=Flask(__name__,static_url_path='/static')

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
    
@app.route('/hashcompare', methods=['GET','POST'])
def hashcompare():
    ctxhash={}
    ctxhash['countries']='''select * from geomaster.paises'''
    ctxhash['cycles']='''select * from jobOrder.ciclos'''
    ctxhash['studies']='''select * from jobOrder.estudios'''
    ctxhash['clients']='''select * from jobOrder.clientes '''
    ctxhash['anios']='''select * from jobOrder.anios '''  
    #ctxhash['meditionTypes']='''SELECT	DISTINCT tipos_medicion FROM jobOrder.sp_mega_job_nf'''
    for val in (ctxhash.keys()):
        v1=ctxhash[val]
        ctxhash[val]=conn._newQuerySelect(v1)
        
    if not request.method == 'GET':
        if ctxhash.keys() not in request.form:
            ctxhash['responseHash'] == 'No hay datos '        
        querySpMegaJob = (f"""SELECT
	    DISTINCT llave_job AS HASHMGJ, ll.tipos_medicion 
        FROM
	    jobOrder.sp_mega_job_nf ll
        WHERE
	    estado_job = 'Activo'
	    AND ciclo = '{cycle}'
	    AND anio = '{anio}'
	    AND pais = '{country}'
	    AND estudio  = '{study}'
	    AND tipos_medicion LIKE '%%'
	    AND empresas LIKE '%{company}%';""")
        
        
        ctxhash['responseHash']=True
        
    return render_template('hash.html',**ctxhash)
    


#from prueba import datos 
@app.route('/test', methods=['GET','POST'])
def test():
    var={}
    var['result']=''
    var['studies']=baseStudiesOperations()
    #http://127.0.0.1:5000/test?Estudio=392
    if request.method=='POST' or request.method=='GET' and (request.args.get('Estudio') != None):
        
        options = int(request.form.get('options') or 0) 
        if options == 1:
            Estudio=request.form.get('idEstudio')
            fechai, fechaf = request.form.get('fechaInicio').replace('-','') ,request.form.get('fechaFin').replace('-','')
        else:
            Estudio=int(request.form.get('Estudio') or request.args.get('Estudio'))
            fechai, fechaf = '',''
        
        nRecords=int(request.form.get('nRecords') or 30)
        #['2023', '09', '13'] exampe date 
        # 0 anio  1 month  2 day    
        resultado = testProcess(tpst='otro', idStudio=Estudio, finicio=fechai, ffin=fechaf, nrecord=nRecords)
        if type(resultado)==list:var['result']=resultado
        else: var['alerts']=resultado
    return render_template('test.html',**var)

@app.route('/studymanager',methods=['GET','POST'])
def StudyManager():
    ctx={}
    ctx['studies']=baseStudiesOperations()
    ctx['rawcsv']=baseStudiesOperations(raw=True)
    ctx['listEst']=conn._newQuerySelect('''select * from jobOrder.estudios''')
    ctx['alert']=request.args.get('w')
    
    if request.method=='POST':
        dataList={}
        dataList['idtabla']=int(request.form.get('idtabla'))
        dataList['estudio']=request.form.get('estudio')
        dataList['descripcion']=request.form.get('descripcion')
        dataList['idestudio']=int(request.form.get('idestudio'))

        ctx['alert']=baseStudiesOperations(operation='w',data=dataList)
        #ctx['alerts']=baseStudiesOperations(operation='w',rd=dataList['rawdata'])

    return render_template('studymanager.html',**ctx)

@app.route('/studydata',methods=['POST'])
def studydata():
    ctx={}
    data=request.form.get('rawdata').replace('\n','').replace('    ','')
    ctx['w']=baseStudiesOperations(operation='w',rd=data)   
    return redirect(url_for('StudyManager' ,**ctx))
    
if __name__=='__main__':
    app.run(debug=True)#host="0.0.0.0", port=80