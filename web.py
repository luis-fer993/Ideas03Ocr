from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import base64
from flask_login import LoginManager
from werkzeug.utils import secure_filename
from main import DataProcess, DB, testProcess, baseStudiesOperations, baseQuery
import pandas as pd
import os
from flask_session import Session
conn= DB()

#import flask

app=Flask(__name__,static_url_path='/static')
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

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
    




@app.route('/test2', methods=['GET','POST'])
def test2():
    var={}
    var['result']={}
    var['studies']=baseStudiesOperations()
    Estudio = request.args.get('estudioid')
    resultado = testProcess(tpst='ambos',idStudio=Estudio, nrecord=30)
    if type(resultado)==dict:
        var['result']=resultado
    else:
        var['alerts']=resultado
    
    if Estudio ==None or '' and request.method=='GET':
        return render_template('prueba.html',**var)
    else:
        return var


#from prueba import datos 
@app.route('/test', methods=['GET','POST'])
def test():
    var={}
    var['result']=''
    var['studies']=baseStudiesOperations()
    #http://127.0.0.1:5000/test?Estudio=392
    if request.method=='POST' or request.method=='GET' and (request.args.get('Estudio') != None and request.args.get('ambiente') != None):
        
        options = int(request.form.get('options') or 0) 
        if options == 1:
            Estudio=request.form.get('idEstudio')
            fechai, fechaf = request.form.get('fechaInicio').replace('-','') ,request.form.get('fechaFin').replace('-','')
        else:
            Estudio=int(request.form.get('Estudio') or request.args.get('Estudio'))
            fechai, fechaf = '',''
        
        #ambiente=request.form.get('ambiente') or request.args.get('ambiente')
        nRecords=int(request.form.get('nRecords') or 30)
        #['2023', '09', '13'] exampe date 
        # 0 anio  1 month  2 day    
        resultado = testProcess( idStudio=Estudio, finicio=fechai, ffin=fechaf, nrecord=nRecords)
        if type(resultado)==dict:var['result']=resultado
        else: var['alerts']=resultado
    return render_template('test.html',**var)

@app.route('/studymanager/',methods=['GET','POST'])
def StudyManager():
    if not session.get('user'):
        return redirect(url_for('test'))
    ctx={}
    ctx['studies']=baseStudiesOperations() #get DataFrame
    ctx['rawcsv']=baseStudiesOperations(raw=True) #get raw File csv
    ctx['listEst']=conn._newQuerySelect('''select * from jobOrder.estudios''') # get list from DB
    ctx['ambienteList']=['pruebas','produccion']
    ctx['alert']=request.args.get('w') #if there is alerts
    ctx['Manager'] =True
    
    if request.method=='POST':
        dataList={}#inputs forms 
        dataList['idtabla']=int(request.form.get('idtabla'))
        dataList['estudio']='' or request.form.get('estudio') 
        dataList['descripcion']='' or request.form.get('descripcion')
        dataList['ambiente']='' or request.form.get('ambiente')
        if request.form.get('idestudio') == 'NoneType': dataList['idestudio']= 000
        else: dataList['idestudio']= request.form.get('idestudio')
        dataList['eliminar']= request.form.get('eliminar')

        ctx['alert']=baseStudiesOperations(operation='w',data=dataList)

    return render_template('studymanager.html',**ctx)

@app.route('/studydata',methods=['POST'])
def studydata():
    ctx={}
    if not request.form.get('newEdit') =='1':
        data=request.form.get('rawdata').replace('\n','').replace('    ','') # replace the new line with nothing
        ctx['w']=baseStudiesOperations(operation='w',rd=data)   #send the information
        return redirect(url_for('StudyManager' ,**ctx)) #redirect to page 
    EstNewData={}
    EstNewData['idtabla']=request.form.get('idtabla')
    EstNewData['estudio']=request.form.get('estudio')
    EstNewData['descripcion']=request.form.get('descripcion')
    EstNewData['idestudio']=request.form.get('idestudio')
    EstNewData['ambiente']='' or request.form.get('ambiente')
    ctx['w']=baseStudiesOperations(operation='n',data=EstNewData)
    return redirect(url_for('StudyManager' ,**ctx))
    
@app.route('/login',methods=['POST','GET'])
def login():
    ctx={}
    if session.get('user')==True:
        return redirect(url_for('StudyManager'))
    if request.method=='POST':
        user = request.form.get('user')
        password = request.form.get('pass') 
        #check if data is correct, password equal to .ven value dencode on b64.
        if user == os.getenv('user') and password == (base64.b64decode(os.getenv('password').encode())).decode(encoding='utf-8'):
            session['user']=True
            return redirect(url_for('StudyManager'))
        else:
            ctx['alerts']='Credenciales Invalidas'
    return render_template('login.html',**ctx)
    
@app.route('/logout')
def logout():
    session['user']=None
    return redirect(url_for('test'))
    
    
@app.errorhandler(404)
def error404(error):
    return render_template('page_not_found.html'),404    
    
if __name__=='__main__':
    app.secret_key=os.getenv('secretKey')
    app.run(debug=True)#host="0.0.0.0", port=80