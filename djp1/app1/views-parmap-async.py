from __future__ import unicode_literals
import sys
import json
import paramiko
import multiprocessing
from app1.models import OSInstanceDJ,OSMasterDJ,SearchWords
from django.shortcuts import render
from django.http import HttpResponse
from app1.forms import OSInstanceForm
from django.forms import formset_factory,modelformset_factory,inlineformset_factory
from gevent.pool import Pool
from functools import partial
import parmap

servers=[{'name':'swiftnode1','ip':'10.0.0.45','serversshport':22},
         {'name':'swiftnode2','ip':'10.0.0.46','serversshport':22},
         {'name':'swiftnode3','ip':'10.0.0.47','serversshport':22},
         {'name':'swiftnode4','ip':'10.0.0.48','serversshport':22}]
numbers = [1, 3, 5,7,9,11,12,13,14,17,18,19]


# Create your views here.
'''
def SearchApi(request):
    #qdict=request.GET
    #timedict={'name':qdict.get("name",""),'empid':qdict.get("empid","")}
    
    #rd=request.read()
    #lst=request.GET.lists()
    #q=request.body.decode("utf-8")
    #j=json.loads(q)
    return HttpResponse("hello")
''' 

def FormSetOSinstVw(request):
    FormSetOSinst=modelformset_factory(OSInstanceDJ,OSInstanceForm,extra=0)
    dtag={}
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
        
        #ftag.append(dtag)
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
                
            ftag = [ctag,dtag]
            rs=mp_handler(ctag,dtag)                       
            #return HttpResponse(dtag['end_second'])
            #return HttpResponse(ftag[0]['end_second'])
            #p = multiprocessing.Pool(processes=4)
            #rs=p.map(AnalyzeServer, ctag)
            #p.close()
            #p.join()
            #rs=AnalyzeServer(ctag,dtag)
            #rsj=json.dumps(rs)
            context={"result":rs}
            return render (request,'seacrh_result.html',context)
            #return HttpResponse(rs)
            
    else:
        formset = FormSetOSinst()
        context = {'formset':formset}           
        return render(request,'os_inst_formset.html',context)
    
#def AnalyzeServer(srvlst=[],tfltr={}):
def AnalyzeServer(srv,tfltr={}):
    #srv=srvwithdatefilter[0]
    #tfltr=srvwithdatefilter[1]
    c1 ='python serverlogparse.py'
    kwordlst=[k['name'] for k in SearchWords.objects.all().values()]
    c3=json.dumps(kwordlst)
    c4=json.dumps(tfltr)
    ssh=paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy()) 
    logs=[]
    all_server_result=[]
    single_server_result={} 
    #for srv in srvlst:
    server_name=srv['name']
    server_ip=srv['ip']
    server_id=srv['serverid']
    server_ssh_port=srv['serversshport']
    #osi=OSInstanceDJ.objects.get(pk=server_id)
    #c2=str(osi.os.logfilename)
    c2="/var/log/syslog*"
    c=c1+" "+"'"+c2+"'"+" "+"'"+c3+"'"+" "+"'"+c4+"'"
    #c="df -k"
    #c='python serverlogparse.py'+' '+"'"+"/var/log/syslog*"+" "+"'["+'"'+"error"+'"]'+'{"'+""
    
    try:
            #sh.connect(server_name,port=server_ssh_port,timeout=1, username='dcim')
            ssh.connect(server_name,port=server_ssh_port,timeout=1, username='dcim',look_for_keys=True,allow_agent=False,key_filename="/root/.ssh/id_dsa")
            stdin, stdout, stderr = ssh.exec_command(c)           
            nlines=0      
            for s in stdout:
                logs.append(s)
                nlines +=1
            if nlines > 1:
                #srv_matched[server_name]=server_ip
                single_server_result['server_name']=server_name
                single_server_result['server_ip']=server_ip
                single_server_result['logs']=logs
                #all_server_result.append(single_server_result)
                #logs=[]
                #single_server_result={}
    except (paramiko.SSHException,paramiko.BadHostKeyException,paramiko.AuthenticationException ) as e:
                single_server_result['server_name']=server_name
                single_server_result['server_ip']=server_ip
                single_server_result['logs']=['Analysis Failed , Check Connection with Log analysis server '+str(e)]
                #all_server_result.append(single_server_result)            
                #single_server_result={}
                #continue
                pass
    
                
            
            #analysis_result.append(',  Next Line:----')
        #return analysis_result,c
        #server_wide_result[server_ip]=analysis_result
        #analysis_result.append(srv['name'])
    #return analysis_result
    return  single_server_result 
#partial_AnalyzeServer = partial(AnalyzeServer, tfltr=RAW_DATASET)

def multi_run_wrapper(args):
   return AnalyzeServer(*args)
def square(number):
    return number * number #all_server_result #srv_matched #server_wide_result['14.142.104.141'] #,analysis_result
def start_process():
    print ' Log Search started with ', multiprocessing.current_process().name
def mp_handler(s,t):
    p = multiprocessing.Pool(processes=4,initializer=start_process)
    #x=p.map(multi_run_wrapper,[(s,t)])
    #x=p.map(partial_AnalyzeServer, t, 1)
    x=parmap.map_async(AnalyzeServer, s, t, chunksize=1).get()
    p.close()
    p.join()
    return x

if __name__ == '__main__':
     y=mp_handler(servers)
     print y
'''
result= {'name':'s1','logs':['l1','l2','l3']},   {'name':'s2','logs':['l4','l5','l6']}    ]

Then context will be like this = {"result":result}

    single_server_result['server_name']=server_name
    single_server_result['server_ip']=server_ip
    single_server_result['server_id']=server_name
    single_server_result['server_ssh_port']=server_ip
ssh.connect(server_name,port=server_ssh_port,timeout=1, username='dcim',look_for_keys=True,allow_agent=False,key_filename="/home/dcim/djp1/djp1/.ssh/id_dsa" )
'''0