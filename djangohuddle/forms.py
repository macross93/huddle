from django import forms
from datetimewidget.widgets import DateTimeWidget, DateWidget, TimeWidget
from events.models import event, user, Document


class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ('description', 'document', )

class EventForm(forms.ModelForm):
    class Meta:
        model = event
        fields = ('name', 'details', 'address', 'city', 'postcode', 'start', 'end', 'charity', 'image')

        widgets = {
            'end': DateTimeWidget(attrs = {'id':'id_dateTimeField', 'placeholder': 'End Time and Date'}, bootstrap_version=3, usel10n=True),
            'start': DateTimeWidget(attrs = {'id':'id_dateTimeField2','placeholder': 'Start Time and Date'}, bootstrap_version=3, usel10n=True),
            'name': forms.TextInput(attrs={'placeholder': 'Event Name'}),
            'details': forms.Textarea(attrs={'placeholder': 'Tell us about your event'}),
            'address': forms.TextInput(attrs={'placeholder': 'Address'}),
            'city': forms.TextInput(attrs={'placeholder': 'City'}),
            'postcode': forms.TextInput(attrs={'placeholder': 'Postcode'}),
            'charity': forms.TextInput(attrs={'placeholder': 'Charity'}),
            'image': forms.TextInput(attrs={'placeholder': 'Image'}),
        }
