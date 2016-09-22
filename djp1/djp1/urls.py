"""djp1 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/dev/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url,include
from django.contrib import admin
from app1 import views
from app1.views import FormSetOSinstVw,get_Job_result,get_server_log,get_server_by_searchid,Search_Screen_Api#,SearchApi
from app1.views import get_server_log_serial,get_server_by_searchid_serial
from app1.views import get_prev_searchid_list_serial

urlpatterns = [
    url('^', include('django.contrib.auth.urls')),
    url(r'^admin/', admin.site.urls,name='admin'),
    url(r'^$',views.FormSetOSinstVw,name='formset-osinst'),
    #url(r'^getjob/(?P<jobid>\w+)/$',views.get_Job_result,name='get-Job')
    url(r'^getjob/(?P<jobid>[\w-]+)/$',views.get_Job_result,name='get-Job'),
    url(r'^getjobapi/(?P<jobid>[\w-]+)/$',views.get_Job_result_serial,name='get-Job-serial'),
    url(r'^getlog/(?P<serverid>[0-9]+)/$',views.get_server_log,name='get-server-log'),
    url(r'^getlogapi/(?P<serverid>[0-9]+)/$',views.get_server_log_serial,name='get-server-log-serial'),
    url(r'^getsrvbysid/(?P<searchid>[0-9]+)/$',views.get_server_by_searchid,name='get-server-by-searchid'),
    url(r'^getsrvbysidapi/(?P<searchid>[0-9]+)/$',views.get_server_by_searchid_serial,name='get-server-by-searchid-serial'),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^search/$',views.Search_Screen_Api,name='Search-Screen-Api'),
    url(r'^getprevsearchesapi/$',views.get_prev_searchid_list_serial,name='get-prev-searchid-list-serial'),          
    url(r'^searchapi/$',views.SearchApi,name='search-api')
]
