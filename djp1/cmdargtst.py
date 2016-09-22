
import sys
import json

x=sys.argv[1]
y=sys.argv[2]
z=sys.argv[3]
print x 
print y 
print z
print '>>>>>>>>going to load second arg in json>>>>>>>>>>>'
jy=json.loads(y)
print jy
print jy[0]
print '++++++going to load 3rd args in json +++++++++++++++++++++++++++++++++'
jz = json.loads(z)
print jz
print jz['start_month']
