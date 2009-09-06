from django import forms
from sillywalks.models import SillyWalk

class SillyWalkForm(forms.ModelForm):
    class Meta:
        model = SillyWalk
        exclude = ('slug',)
