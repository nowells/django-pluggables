from django import forms
from complaints.models import Complaint

class ComplaintForm(forms.ModelForm):
    def save(self, request=None, *args, **kwargs):
        kwargs['commit'] = False
        obj = super(ComplaintForm, self).save(*args, **kwargs)
        obj.save(request)
        return obj

    class Meta:
        model = Complaint
        exclude = ('pluggable_content_type', 'pluggable_object_id',)
