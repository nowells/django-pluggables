from django import forms
from complaints.models import Complaint

class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        exclude = ('pluggable_content_type', 'pluggable_object_id',)
