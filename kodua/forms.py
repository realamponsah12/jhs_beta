from django_summernote.widgets import SummernoteWidget, SummernoteInplaceWidget
from django import forms
from .models import IssueTracker

class IssueTrackerForms(forms.ModelForm):
    class Meta:
        model = IssueTracker
        fields = ['title', 'content']
        widgets = {'content': SummernoteWidget()}