from django import forms

from events.models import event

class eventForm(forms.ModelForm):

    class Meta:
        model = event
        fields = ('name','details')
#        fields = ('name', 'details', 'address', 'city', 'postcode', 'start', 'end', 'duration', 'charity')
