from django.contrib import admin
from app1.models import OSMasterDJ,OSInstanceDJ,SearchWords,SearchID,ResultServer,SearchLogs4

# Register your models here.

class OSMasterDJdeco(admin.ModelAdmin):
    list_display = ('name','logfilename')
    
class OSInstanceDJdeco(admin.ModelAdmin):
    list_display = ('name','ip','os','sshport')
    
admin.site.register(OSMasterDJ,OSMasterDJdeco)
admin.site.register(OSInstanceDJ,OSInstanceDJdeco)
admin.site.register(SearchWords)
admin.site.register(SearchID)
admin.site.register(ResultServer)
admin.site.register(SearchLogs4)