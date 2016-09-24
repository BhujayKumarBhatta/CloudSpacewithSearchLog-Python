'''
Bhujay Kumar Bhatta
'''

from __future__ import unicode_literals
from __future__ import absolute_import
import sys
import json
from decimal import Decimal
import paramiko
import datetime
from django.contrib.auth.decorators import login_required, permission_required
from django.utils import timezone
from app1.models import OSInstanceDJ,OSMasterDJ,SearchWords,SearchID,ResultServer,SearchLogs4
from django.shortcuts import render
from django.http import HttpResponse
from app1.forms import OSInstanceForm
from django.forms import formset_factory,modelformset_factory,inlineformset_factory
import socket
from celery import Celery , shared_task , task
from celery.result import AsyncResult
#from djp1.djcelery import app
from djp1.celery import app


from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework import status
from rest_framework.decorators import api_view ,authentication_classes,permission_classes
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from app1.serializers import OSInstanceDJSerial,OSMasterDJSerial,SearchWordsSerial,SearchIDSerial,ResultServerSerial,SearchLogs4Serial


'''
class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)
'''

'''
app = Celery('djp1',
             broker='amqp://',
             backend='rpc://')
             
'''

# Create your views here.

@login_required
def FormSetOSinstVw(request):
    FormSetOSinst=modelformset_factory(OSInstanceDJ,OSInstanceForm,extra=0)
    ctag = []
    ftag = []        
    if request.method == 'POST':
        dtag={'start_month':request.POST.get("month",""),
                              'start_date':int(request.POST.get("startdate","")),
                              'end_date':int(request.POST.get("enddate","")),
                              'start_hour':int(request.POST.get("starthour",0)),
                              'end_hour':int(request.POST.get("endhour",24)),
                              'start_minute':int(request.POST.get("startminute",0)),
                              'end_minute':int(request.POST.get("endminute",60)),
                              'start_second':int(request.POST.get("startsecond",0)),
                              'end_second':int(request.POST.get("endsecond",60))}
        
        ftag.append(dtag)
        #return HttpResponse(dtag['endsecond'])        #'''
        
        formset = FormSetOSinst(request.POST,request.FILES)        
        if formset.is_valid():            
            tmpformset = formset.save(commit=False)
            for tmpform in tmpformset:
                    #if tmpform.selected == True:
                        
                        rec = {'name':tmpform.name,'ip':tmpform.ip,
                               'serverid':tmpform.id,'serversshport':tmpform.sshport} #'Selection_Status':tmpform.selected
                        #rec = tmpform.ip
                        #tmpform.save()
                        ctag.append(rec)
                
            ftag.append(ctag)            
            if request.user.is_authenticated():
                unm=request.user.username
            else:
                unm = 'anonymous'            
            job=AnalyzeServer.delay(unm,ctag,dtag)
            context={"jobid":job.id,"Jobstatus":job.state}
            return render (request,'response_after_job_post.html',context)
            #return HttpResponse("Job Id :- "+ job.id +"  Job Status : -  " + job.state)
            
    else:
        formset = FormSetOSinst()
        context = {'formset':formset}           
        return render(request,'os_inst_formset.html',context)
    
def get_Job_result(request,jobid):           
    job = AsyncResult(jobid,app=app)
    if job.ready():      
        #data = json.dumps(job.result)
        data = job.result
        #d=json.dumps(data)
        context={"result":data,"prev_searches":SearchID.objects.all()}
        return render (request,'seacrh_result_severwise.html',context)
    else:
        d="Job status is "+job.state +" please wait for a while and  click on browser  refresh button  again"
        return HttpResponse(d)
    
    
def get_server_log(request,serverid):
    srv=ResultServer.objects.get(pk=serverid)
    srvlog=srv.searchlogs4_set.all()
    context={"srvlog":srvlog}
    return render (request,'severwise_logs.html',context)


def get_server_by_searchid(request,searchid):
    sid=SearchID.objects.get(pk=searchid)
    data={'sid':sid,'resultservers':sid.resultserver_set.all()} 
    context={"result":data,"prev_searches":SearchID.objects.all()}
    return render (request,'seacrh_result_severwise.html',context)

@app.task 
#@app.task(bind=True) 
#@task(name='djp1.views.AnalyzeServer') 
#@shared_task
#@task
def AnalyzeServer(uname,srvlst=[],tfltr={}):
    sid=SearchID(searchedby=uname) #'anonymous'
    sid.save()
    print sid
    c1 ='python serverlogparse.py'
    #Get Search keyword list from Database and convert to string for command line argument
    kwordlst=[k['name'] for k in SearchWords.objects.all().values()]    
    c3=json.dumps(kwordlst)
    #Get the time filter values
    c4=json.dumps(tfltr)    
    #initialize SSH objects
    ssh=paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())   
    logs=[]
    for srv in srvlst:
        server_name=srv['name']
        server_ip=srv['ip']
        server_id=srv['serverid']
        server_ssh_port=srv['serversshport']
        osi=OSInstanceDJ.objects.get(pk=server_id)
        c2=str(osi.os.logfilename)
        c=c1+" "+"'"+c2+"'"+" "+"'"+c3+"'"+" "+"'"+c4+"'"
        store_srv_in_db=ResultServer(osinstance=osi,searchid=sid,name=osi.name,ip=osi.ip)
        #store_srv_in_db=ResultServer(osinstance=osi,searchid=sid)
        store_srv_in_db.save()
        rs=sid.resultserver_set.all()
        rsar=[]
        rsdict={}
        for r in rs:
            rsdict['id']=r.id
            rsdict['name']=r.name
            rsdict['ip']=r.ip
            rsar.append(rsdict)       
            
        #jrs=json.dumps(rs)
        #c='python serverlogparse.py'+' '+"'"+"/var/log/syslog*"+" "+"'["+'"'+"error"+'"]'+'{"'+""
        try:
            ssh.connect(server_name,port=server_ssh_port,timeout=1, username='dcim')
            #ssh.connect(server_name,port=server_ssh_port,timeout=1, username='dcim',look_for_keys=True,allow_agent=False,key_filename="/home/dcim/djp1/djp1/.ssh/id_dsa" )
            stdin, stdout, stderr = ssh.exec_command(c)           
            nlines=0      
            for s in stdout:
                saved_log_in_db=SearchLogs4(rserver=store_srv_in_db,logline=s)
                saved_log_in_db.save()
                logs.append(s)
                nlines +=1
            if nlines > 1:                          
                logs=[]                
        except (paramiko.SSHException,paramiko.BadHostKeyException,paramiko.AuthenticationException,socket.error ) as e:
                emsg='Analysis Failed due to '+'Exception Type :- '+str(e)                  
                saved_log_in_db=SearchLogs4(rserver=store_srv_in_db,logline=emsg)
                saved_log_in_db.save()
                continue 
                           
    #return {'sid':sid,'resultservers':rs}      
    #return {'sid':"123"}
    zo= {'sid':sid.id,'resultservers':rsar}
    return zo
'''
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
API RELATED VIEWS STARTS HERE
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
'''


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes((SessionAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
def Search_Screen_Api(request,format=json):
    """
    List of servers to be selected and search submission
    """
    if request.method == 'GET':
        osins = OSInstanceDJ.objects.all()
        serializer = OSInstanceDJSerial(osins, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        q=request.body.decode("utf-8")
        dtag=json.loads(q)
        ctag=dtag['srvlst']
        if request.user.is_authenticated():
                unm=request.user.username
        else:
                unm = 'anonymous'            
        job=AnalyzeServerSerial.delay(unm,ctag,dtag)
        context={"jobid":job.id,"jobstatus":job.state}
        context1=json.dumps(context)
        #return HttpResponse(dtag['srvlst'])
        return HttpResponse(context1)
        '''
        data = JSONParser().parse(request)
        serializer = OSInstanceDJSerial(data=data)
        if serializer.is_valid():
            serializer.save()
            return JSONResponse(serializer.data, status=201)
        return JSONResponse(serializer.errors, status=400)
        '''

@api_view(['GET'])    
def get_Job_result_serial(request,jobid):           
    job = AsyncResult(jobid,app=app)
    if job.ready():      
        data = job.result
        #d=json.dumps(data)
        ps=SearchID.objects.all()
        serializer=SearchIDSerial(ps,many=True)
        context={"result":data,"prev_searches":serializer.data,"Job_status":job.state}
        #return HttpResponse(context)
        #return JSONResponse(serializer.data)
        #return JSONResponse(data)
        
    else:
        data="Search is still going on in the background , click on this job id after some time to see the  result"
        context={"result":data,"Job_status":job.state}
        #return HttpResponse(d)
    #contextj=json.dumps(context)
    return Response(context)

@api_view(['GET'])
def get_server_log_serial(request,serverid):
    srv=ResultServer.objects.get(pk=serverid)
    srvlog=srv.searchlogs4_set.all()
    serializer=SearchLogs4Serial(srvlog,many=True)
    context={"srvlog":serializer.data}
    return Response(context)

@api_view(['GET'])
def get_server_by_searchid_serial(request,searchid):
    sid=SearchID.objects.get(pk=searchid)    
    resultservers=sid.resultserver_set.all()
    serializer = ResultServerSerial(resultservers, many=True)
    #serializer1=SearchIDSerial(sid)              
    #data= {'sid':serializer1.data,'resultservers':serializer.data} 
    context= {'resultservers':serializer.data}     
    #ps=SearchID.objects.all()
    #serializer2=SearchIDSerial(ps,many=True)
    #context={"result":data,"prev_searches":serializer2.data}
    return Response(context)

@api_view(['GET'])
def get_prev_searchid_list_serial(request):
    ps=SearchID.objects.all()
    serializer2=SearchIDSerial(ps,many=True)
    context={"prev_searches":serializer2.data}
    return Response(context)


@app.task   
def AnalyzeServerSerial(uname,srvlst=[],tfltr={}):
    sid=SearchID(searchedby=uname) #'anonymous'
    sid.save()
    print sid
    c1 ='python serverlogparse.py'
    #Get Search keyword list from Database and convert to string for command line argument
    kwordlst=[k['name'] for k in SearchWords.objects.all().values()]    
    c3=json.dumps(kwordlst)
    #Get the time filter values
    c4=json.dumps(tfltr)    
    #initialize SSH objects
    ssh=paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())   
    logs=[]
    for srv in srvlst:
        server_name=srv['name']
        server_ip=srv['ip']
        server_id=srv['id']
        server_ssh_port=srv['sshport']
        osi=OSInstanceDJ.objects.get(pk=server_id)
        c2=str(osi.os.logfilename)
        c=c1+" "+"'"+c2+"'"+" "+"'"+c3+"'"+" "+"'"+c4+"'"
        store_srv_in_db=ResultServer(osinstance=osi,searchid=sid,name=osi.name,ip=osi.ip)
        store_srv_in_db.save()
        #c='python serverlogparse.py'+' '+"'"+"/var/log/syslog*"+" "+"'["+'"'+"error"+'"]'+'{"'+""
        try:
            ssh.connect(server_name,port=server_ssh_port,timeout=1, username='dcim')
            #ssh.connect(server_name,port=server_ssh_port,timeout=1, username='dcim',look_for_keys=True,allow_agent=False,key_filename="/home/dcim/djp1/djp1/.ssh/id_dsa" )
            stdin, stdout, stderr = ssh.exec_command(c)           
            nlines=0      
            for s in stdout:
                saved_log_in_db=SearchLogs4(rserver=store_srv_in_db,logline=s)
                saved_log_in_db.save()
                logs.append(s)
                nlines +=1
            if nlines > 1:                          
                logs=[]                
        except (paramiko.SSHException,paramiko.BadHostKeyException,paramiko.AuthenticationException,socket.error ) as e:
                emsg='Analysis Failed due to '+'Exception Type :- '+str(e)                  
                saved_log_in_db=SearchLogs4(rserver=store_srv_in_db,logline=emsg)
                saved_log_in_db.save()
                continue 
    #osins = OSInstanceDJ.objects.all()
    resultservers=sid.resultserver_set.all()
    serializer = ResultServerSerial(resultservers, many=True)
    serializer1=SearchIDSerial(sid)
    #return serializer.data
    #return JSONResponse(serializer.data)                   
    jo={'sid':serializer1.data,'resultservers':serializer.data}
    return json.dumps(jo)      



@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes((SessionAuthentication, BasicAuthentication))
#@permission_classes((IsAuthenticated,))
def SearchApi(request):
    '''
    qdict=request.GET
    timedict={'name':qdict.get("name",""),'empid':qdict.get("empid","")}
    '''
    #rd=request.read()
    #lst=request.GET.lists()
    #q=request.body.decode("utf-8")
    #q=request.body
    #j=json.loads(q)
    #k=j['srvlst']
    #s='Your user name is :'+k[0]['name']
    if request.user.is_authenticated():
                unm=request.user.username +" has been successfully authenticated"
    else:
                unm = 'failed to Authenticate hence switched to anonymous'   
    #s='Your user name is :'+request.user.username
    s=unm
    return  HttpResponse(s) #None

    

'''
result= {'name':'s1','logs':['l1','l2','l3']},   {'name':'s2','logs':['l4','l5','l6']}    ]

Then context will be like this = {"result":result}
'''