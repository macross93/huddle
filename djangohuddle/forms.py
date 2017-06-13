from django import forms

from events.models import event

class eventForm(forms.ModelForm):

    class Meta:
        model = event
        fields = ('name', 'image', 'details', 'address', 'city', 'postcode', 'start', 'end', 'duration', 'charity')

class PostForm(forms.ModelForm):

    class Meta:
        model = user
        fields = ('facebook_id',)
