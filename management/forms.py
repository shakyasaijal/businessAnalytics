from django import forms
from leave_manager import models as leave_models


class DateInput(forms.DateInput):
    input_type = 'date'


class HolidayForm(forms.ModelForm):
    from_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    to_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    title = forms.CharField(
        label='Title *',
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter Holiday Title', 'autocomplete': 'off'
        }),
    )
    description = forms.CharField(
        label='Description',
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter Description if any', 'autocomplete': 'off'
        }),
    )
    class Meta:
        model = leave_models.Holiday
        fields = ('from_date', 'to_date', 'title', 'description', 'branch')
        