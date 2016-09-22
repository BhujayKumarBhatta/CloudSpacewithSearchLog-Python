'''
Created on Jul 19, 2016

@author: Bhujay
'''
import sys
import glob
import gzip,bz2
import re
import json

def search_in_file(file_name,kword=[]):
    '''
    input: - file name with full path and list of keywords to be searched.
    first define a list with comma separated keywords and pass the list as argument
    output : - is a list with all comma separated lines that contains the keywords
    
    '''
    try:
        with open(file_name)as f:
            errorsInfile=[]
            for l in f:
                try:
                    for k in kword:
                        if k in l:
                            errorsInfile.append(l)
                except ValueError:
                    continue
        return errorsInfile
    except IOError as err:
        return "could not find a file by the name" , file_name


def get_all_logs(filename_pattern):
    log_files = glob.glob(filename_pattern)
    for fname in log_files:
        if fname.endswith(".gz"):
            yield gzip.open(fname)
        elif fname.endswith(".bz2"):
            yield bz2.BZ2File(fname)
        else:
            yield open(fname)
    pass

    
def get_error_lines(log_files,kword=[]):
    for f in log_files:
        for l in f:
                try:
                    for k in kword:
                        if k in l:
                            yield l
                except ValueError:
                    continue
def field_map(dictseq,name,func):
    for d in dictseq:
        d[name] = func(d[name])
        yield d
       

def full_error_search(path_n_file_patterns,kword=[],sf={}):
    pats=re.compile(r'''\s* #skip leading white space , * means it may or may not be there
                     (?P<month>\S+) #Months , Any value till white space
                     \s* #skip white space if present , * helps both condition
                     (?P<day>\d+)   #day , numeric digit , how to make it two digit?
                     \s* #skip white space
                     (?P<hour>\d+)   #Hour
                     \W* #skip white space
                     (?P<minutes>\d+)   #Minutes
                     \W* #skip white space
                     (?P<seconds>\d+)   #Seconds
                     \s* #skip white space
                     (?P<mbody> .*)   #Seconds , rest all from the line
                        ''',re.VERBOSE)
    all_logs=get_all_logs(path_n_file_patterns)
    all_errors=get_error_lines(all_logs,kword)
    all_errors_regex=(pats.match(l) for l in all_errors)
    all_error_reg_group=(g.group() for g in all_errors_regex)
    all_error_dict=(g.groupdict() for g in all_errors_regex)
    all_error_dict_fieldmap=field_map(all_error_dict,'day',int)
    all_error_dict_fieldmap=field_map(all_error_dict_fieldmap,'hour',int)
    all_error_dict_fieldmap=field_map(all_error_dict_fieldmap,'minutes',int)
    all_error_dict_fieldmap=field_map(all_error_dict_fieldmap,'seconds',int)
    for k in all_error_dict_fieldmap:
        if sf['start_month']=='ALL':
            if (
                  (sf['start_date']<=k['day']<=sf['end_date']) and
                  (sf['start_hour']<=k['hour']<= sf['end_hour'])  and 
                  (sf['start_minute']<=k['minutes']<=  sf['end_minute'])and 
                  (sf['start_second']<=k['seconds']<= sf['end_second'])
                  ) :
                    print '%s %d %d:%d:%d %s' % (k['month'],k['day'],k['hour'],k['minutes'],k['seconds'],k['mbody'])
        else:
            if (
                  (k['month']== sf['start_month']) and
                  (sf['start_date']<=k['day']<=sf['end_date']) and
                  (sf['start_hour']<=k['hour']<= sf['end_hour'])  and 
                  (sf['start_minute']<=k['minutes']<=  sf['end_minute'])and 
                  (sf['start_second']<=k['seconds']<= sf['end_second'])
                  ) :
                    print '%s %d %d:%d:%d %s' % (k['month'],k['day'],k['hour'],k['minutes'],k['seconds'],k['mbody'])

if __name__ == '__main__':
        '''
        path_n_file_pattern_array ='/var/log/syslog*'
        kword1=['error', 'warning', 'alert']
        time_filter={'start_month':'ALL','start_date':0,'end_date':31,'start_hour':0,
                     'end_hour':24,'start_minute':0,'end_minute':60,'start_second':0,'end_second':60}
         
        '''
        path_n_file_pattern_array = sys.argv[1]
        kword1= json.loads(sys.argv[2])
        time_filter = json.loads(sys.argv[3])
        
        full_error_search(path_n_file_pattern_array,kword1,time_filter) 


'''
python serverlogparse.py '/var/log/syslog*'  '["error", "warning", "alert"]'  '{"start_month":"ALL","start_date":0,"end_date":31,"start_hour":0,"end_hour":24,"start_minute":0,"end_minute":60,"start_second":0,"end_second":60}'
'''

'''
c1 ='python serverlogparse.py'
c2='/var/log/syslog*'
kword=["error", "warning", "alert"]
c3=str(kword)
timefileter={"start_month":"ALL","start_date":0,"end_date":31,"start_hour":0,"end_hour":24,"start_minute":0,"end_minute":60,"start_second":0,"end_second":60}
c4=str(timefileter)
c=c1+" "+"'"+c2+"'"+" "+"'"+c3+"'"+" "+"'"+c4+"'"
ssh.connect('dcim',port=2223, username='dcim')
stdin, stdout, stderr = ssh.exec_command(c)

'''


  
'''
if (k['month']==start_month and  (start_date<=k['day']<=end_date) and
      start_hour<=k['hour']<= end_hour  and start_minute<=k['minutes']<=  end_minute) :

character class [abc], [a-z],[^a],- excluding a [\] - special character within the bracket looses their meta property

\  meta to strip off the special meaning e.g \\ or \[


>>> from serverlogparse import get_all_logs,get_error_lines
>>> all_logs=get_all_logs('/var/log/syslog*')
>>> kword=['error','warning','alert']
>>> all_errors=get_error_lines(all_logs,kword)
>>> for el in all_errors:
...  print el
... 

col_name=['month','day','hour','host','errorsource','severity','msgbody']
all_logs=get_all_logs('/var/log/syslog*')
all_errors=get_error_lines(all_logs,kword)
all_errors_split=[l.split(' ' ,8) for l in all_errors]
all_errors_zip=(zip(col_name,v) for v in all_errors_split)
all_errors_dict=dict(zip(col_name,v) for v in all_errors_split)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
ValueError: dictionary update sequence element #0 has length 7; 2 is required
>>> 
logpats = r'(\S+) (\S+) (\S+) \[(.*?)\] '\
          r'"(\S+) (\S+) (\S+)" (\S+) (\S+)'


all_logs=get_all_logs('/var/log/syslog*')
all_errors=get_error_lines(all_logs,kword)
all_errors_regex=(pats.match(l) for l in all_errors)
all_error_reg_group=(g.group() for g in all_errors_regex)
all_error_dict=(g.groupdict() for g in all_errors_regex)
all_error_dict_fieldmap=field_map(all_error_dict,'day',int)
all_error_dict_fieldmap=field_map(all_error_dict_fieldmap,'hour',int)
all_error_dict_fieldmap=field_map(all_error_dict_fieldmap,'minutes',int)
all_error_dict_fieldmap=field_map(all_error_dict_fieldmap,'seconds',int)
for k in all_error_dict_fieldmap:
       if k['day'] == '9':
           print k['day']


                    


HOW to CREATE A DICTIONARY  AND RETRIEVE VALUE
>>> a=('drink', 'food','color')
>>> b=('water','bread','red')
>>> c=zip(a,b)
>>> c
[('drink', 'water'), ('food', 'bread'), ('color', 'red')]
>>> 
>>> d
{'food': 'bread', 'color': 'red', 'drink': 'water'}
>>> 
>>> d['food']
'bread'


all_logs=get_all_logs('/var/log/syslog*')
all_errors=get_error_lines(all_logs,kword)
all_errors_regex=(pats.match(l) for l in all_errors)
all_error_reg_group=(g.group() for g in all_errors_regex)
all_error_dict=(g.groupdict() for g in all_errors_regex)
all_error_dict_fieldmap=field_map(all_error_dict,'day',int)
for k in all_error_dict_fieldmap:
  if k['day'] >13:
   print k

from serverlogparse import get_all_logs ,get_error_lines,field_map,full_error_search
path_n_file_pattern_array ='/var/log/syslog*'
kword1=['error', 'warning', 'alert']
time_filter={'start_month':'ALL','start_date':0,'end_date':31,'start_hour':0,
'end_hour':24,'start_minute':0,'end_minute':60,'start_second':0,'end_second':60} 
full_error_search(path_n_file_pattern_array,kword1,time_filter)
'''
             
'''
=====================================================
Executing the program in remote server
===============================================
import paramiko
ssh=paramiko.SSHClient()
ssh.load_system_host_keys()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('dcim',port=2223, username='dcim')
stdin, stdout, stderr = ssh.exec_command("df -k")
stdout.readline()   # stdout.read() # to read the entire line
stdout.next()

# how do we copy or scp the python program to the  target server?
# this exec command runs only when the py file is pressent on the home directory of the user by which ssh was done
stdin, stdout, stderr = ssh.exec_command("python serverlogparse.py")
stdout.readline()

======================================
when asked password 
stdin.write('lol\n')
stdin.flush()

============================
call python script in another way 

cat serverlogparse.py| ssh -p 2223 dcim@dcim python -

===================

install ssh apt-get install ssh
service ssh restart 
first connect with password 
ssh username@username.suso.org

The authenticity of host 'arvo.suso.org (216.9.132.134)' can't be established. 
RSA key fingerprint is 53:b4:ad:c8:51:17:99:4b:c9:08:ac:c1:b6:05:71:9b. 
Are you sure you want to continue connecting (yes/no)? yes 
Warning: Permanently added 'arvo.suso.org' (RSA) to the list of known hosts.

from the source machine generate key ssh-keygen -t dsa

copy the public key in target machine scp ~/.ssh/id_dsa.pub username@arvo.suso.org:.ssh/authorized_keys
we can login now without password 

chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
cat ~/.ssh/id_dsa.pub

ssh-copy-id yourusername@your.website.com

'''             
