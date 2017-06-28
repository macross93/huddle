from django import forms

from events.models import event, user, Document


class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ('description', 'document', )

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ('name', 'details', 'address', 'city', 'postcode', 'start', 'end', 'duration', 'charity', 'image', 'volunteer', 'confirmed')
