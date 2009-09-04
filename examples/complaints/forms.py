from django import forms
from complaints.models import Complaint

class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
