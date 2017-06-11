from django import forms

from events.models import event

class eventForm(forms.ModelForm):

    class Meta:
        model = event
	fields = ('name')
#        fields = ('name', 'details', 'address', 'city', 'postcode', 'start', 'end', 'duration', 'charity')
