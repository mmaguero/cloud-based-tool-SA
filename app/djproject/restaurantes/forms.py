# -*- coding: utf-8 -*-
from django import forms

class ComputeForm(forms.Form):
  title       = forms.CharField(required=True, label='Title')
  description = forms.CharField(required=True, label='Review', widget=forms.Textarea)
