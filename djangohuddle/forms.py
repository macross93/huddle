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

        end = forms.DateTimeField(widget=DateTimeWidget(usel10n=True, bootstrap_version=3))
        start = forms.DateTimeField(widget=DateTimeWidget(usel10n=True, bootstrap_version=3))

        widgets = {
            'end': DateTimeWidget(attrs = {'id':'id_dateTimeField'}, bootstrap_version=3, usel10n=True),
            'start': DateTimeWidget(attrs = {'id':'id_dateTimeField'}, bootstrap_version=3, usel10n=True),
        }
