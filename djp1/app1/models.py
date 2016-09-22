from __future__ import unicode_literals

from django.db import models
from django.utils import timezone

# Create your models here.
class OSMasterDJ(models.Model):
    name=models.CharField(max_length=100)
    logfilename=models.CharField(max_length=100)    
    def __unicode__(self):
        return self.name
    


class OSInstanceDJ(models.Model):
    name=models.CharField(max_length=100)
    ip=models.CharField(max_length=16)
    os=models.ForeignKey(OSMasterDJ)
    sshport = models.IntegerField(default = 22)    
    def __unicode__(self):
        return self.name

class SearchWords(models.Model):
    name=models.CharField(max_length=100)    
    def __unicode__(self):
        return self.name
    
class SearchID(models.Model):
    searchedby=models.CharField(max_length=100)
    searchdate=models.DateTimeField(default=timezone.now)
    created=models.DateTimeField(editable=False,default=timezone.now)        
    def __unicode__(self):
        return str(self.id)
    
  
class ResultServer(models.Model):
    osinstance=models.ForeignKey(OSInstanceDJ)
    name=models.CharField(max_length=100,null=True)
    ip=models.CharField(max_length=19,null=True)
    searchid=models.ForeignKey(SearchID)
    def __unicode__(self):
        return str(self.id)
    
class SearchLogs4(models.Model):
    rserver=models.ForeignKey(ResultServer)
    logline=models.CharField(max_length=2000)       
    def __unicode__(self):
        return str(self.id) 
    
