'''
Created on Sep 3, 2016

@author: cisco
'''
from rest_framework import serializers
#from snippets.models import Snippet, LANGUAGE_CHOICES, STYLE_CHOICES
from app1.models import OSInstanceDJ,OSMasterDJ,SearchWords,SearchID,ResultServer,SearchLogs4
from django.utils import timezone

class OSMasterDJSerial(serializers.ModelSerializer):
    class Meta:
        model=OSMasterDJ
        fields = ('name', 'logfile')
    


class OSInstanceDJSerial(serializers.ModelSerializer):
    class Meta:
        model=OSInstanceDJ
        fields='__all__'    
    

class SearchWordsSerial(serializers.ModelSerializer):
    class Meta:
        model=SearchWords
        fields='__all__'  
    
class SearchIDSerial(serializers.ModelSerializer):
    class Meta:
        model=SearchID
        fields='__all__'  
    
  
class ResultServerSerial(serializers.ModelSerializer):
    class Meta:
        model=ResultServer
        fields = ('name','ip','osinstance','id')  
    
class SearchLogs4Serial(serializers.ModelSerializer):
    class Meta:
        model=SearchLogs4
        fields='__all__'  