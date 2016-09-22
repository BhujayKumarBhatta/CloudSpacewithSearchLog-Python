from __future__ import unicode_literals
from __future__ import absolute_import
import sys
import json
import paramiko
import datetime
from django.utils import timezone
from app1.models import OSInstanceDJ,OSMasterDJ,SearchWords,SearchID,ResultServer,SearchLogs4
from django.shortcuts import render
from django.http import HttpResponse
from app1.forms import OSInstanceForm
from django.forms import formset_factory,modelformset_factory,inlineformset_factory
import socket
from celery import Celery , shared_task
from celery.result import AsyncResult
#from djp1.djcelery import app
from djp1.celery import app
'''
app = Celery('djp1',
             broker='amqp://',
             backend='rpc://')
             
'''

# Create your views here.


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
            #return HttpResponse(dtag['end_second'])
            #return HttpResponse(ftag[0]['end_second'])
            #rs=AnalyzeServer.delay(ctag,dtag)
            #sid=SearchID(searchedby='annonymus')
            #sid.save()
            #print sid
            job=AnalyzeServer.delay(ctag,dtag)
            #job=testsid.delay()              
            #rsj=json.dumps(rs)
            context={"jobid":job.id,"Jobstatus":job.state}
            return render (request,'response_after_job_post.html',context)
            #return HttpResponse("Job Id :- "+ job.id +"  Job Status : -  " + job.state)
            
    else:
        formset = FormSetOSinst()
        context = {'formset':formset}           
        return render(request,'os_inst_formset.html',context)
    
def get_Job_result(request,jobid):
    """ A view to report the progress to the user 
    if 'job' in request.GET:
        job_id = request.GET['job']
    else:
        return HttpResponse('No job id given.')
        app = Celery('djp1',
             broker='amqp://',
             backend='rpc://')        
    """
       
    job = AsyncResult(jobid,app=app)
    if job.ready():      
        data = job.result
        #d=json.dumps(data)
        context={"result":data}
        return render (request,'seacrh_result.html',context)
    else:
        d="Job status is "+job.state +" please wait for a while and  click on browser  refresh button  again"
        return HttpResponse(d)
    
    #return HttpResponse(json.dumps(data), mimetype='application/json')
#@shared_task 
@app.task   
def AnalyzeServer(srvlst=[],tfltr={}):
    # Actual program name to be placed on all servers ssh users home directory
    #c1 ='python cmdargtst.py'
    #t=datetime.datetime.now()
    sid=SearchID(searchedby='Search program analyze server')
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
    
    #Extract server id ,  name and ip  from the list of servers selected by user 
    #Get the log file name from the OS master using server id  and store it in c2
    #construct the whole command  line with argument  to pass string version python list and dictionary objects 
    # within serverlogparse program who can convert it as json object
    #connect to each server and store the  the log file in a list
    logs=[]
    #srv_matched={}
    all_server_result=[]
    single_server_result={} 
    for srv in srvlst:
        server_name=srv['name']
        server_ip=srv['ip']
        server_id=srv['serverid']
        server_ssh_port=srv['serversshport']
        osi=OSInstanceDJ.objects.get(pk=server_id)
        c2=str(osi.os.logfilename)
        c=c1+" "+"'"+c2+"'"+" "+"'"+c3+"'"+" "+"'"+c4+"'"
        store_srv_in_db=ResultServer(osinstance=osi,searchid=sid)
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
                #srv_matched[server_name]=server_ip
                #store_srv_in_db=ResultServer(osinstance=osi,searchid=sid)
                single_server_result['server_name']=server_name
                single_server_result['server_ip']=server_ip
                single_server_result['logs']=logs
                all_server_result.append(single_server_result)
                logs=[]
                single_server_result={}
        except (paramiko.SSHException,paramiko.BadHostKeyException,paramiko.AuthenticationException,socket.error ) as e:
                single_server_result['server_name']=server_name
                single_server_result['server_ip']=server_ip
                emsg='Analysis Failed due to '+'Exception Type :- '+str(e)
                single_server_result['logs']=[emsg]
                '''
                single_server_result['logs']=['Analysis Failed due to '+
                                              'Exception Type :- '+str(e)]
                                              '''
                all_server_result.append(single_server_result)            
                single_server_result={}
                saved_log_in_db=SearchLogs4(rserver=store_srv_in_db,logline=emsg)
                saved_log_in_db.save()
                continue
                
            
            #analysis_result.append(',  Next Line:----')
        #return analysis_result,c
        #server_wide_result[server_ip]=analysis_result
        #analysis_result.append(srv['name'])
    #return analysis_result
    return   all_server_result #srv_matched #server_wide_result['14.142.104.141'] #,analysis_result

@app.task
def add(x, y):
    return x + y

@app.task
def testsid():
    sid=SearchID(searchedby='testsid program')
    sid.save()
    print sid

def SearchApi(request):
    '''
    qdict=request.GET
    timedict={'name':qdict.get("name",""),'empid':qdict.get("empid","")}
    '''
    #rd=request.read()
    #lst=request.GET.lists()
    #q=request.body.decode("utf-8")
    #j=json.loads(q)
    return None# HttpResponse(rd)
    

'''
result= {'name':'s1','logs':['l1','l2','l3']},   {'name':'s2','logs':['l4','l5','l6']}    ]

Then context will be like this = {"result":result}
'''