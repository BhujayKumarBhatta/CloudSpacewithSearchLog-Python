from __future__ import unicode_literals

from django.db import models

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
    searchdate=models.DateField()        
    def __unicode__(self):
        return str(self.id)
    
class ResultServer1(models.Model):
    name=models.CharField(max_length=100)  
    osinstance=models.ForeignKey(OSMasterDJ)
    searchid=models.ForeignKey(SearchID)
    def __unicode__(self):
        return str(self.id)
   
class SearchLogs1(models.Model):
    rserver=models.ForeignKey(ResultServer1)
    seacrhlog=models.CharField(max_length=2000)       
    def __unicode__(self):
        return str(self.id)
