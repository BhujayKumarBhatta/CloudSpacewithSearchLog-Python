'''
Created on Jul 24, 2016

@author: bhujay
'''

from django import forms
from django.forms import  ModelForm, formset_factory
from django.forms import Textarea,CheckboxInput,SelectMultiple
from app1.models import OSInstanceDJ,OSMasterDJ


class OSInstanceForm(ModelForm):
    selected = forms.BooleanField(label = 'Select', required=False)
    class Meta:
        model=OSInstanceDJ
        #fields='__all__'
        exclude = ['os']
        
       
        