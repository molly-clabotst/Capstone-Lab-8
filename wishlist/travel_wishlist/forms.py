from django import forms
from django.forms import FileInput, DateInput
from .models import Place

class NewPlaceForm(forms.ModelForm):
    class Meta:
        model = Place
        fields = ('name', 'visited')

class DateInpu(forms.DateInput):
    input_type = 'date'

class TripReviewForm(forms.ModelForm):
    class Meta:
        model = Place
        fields = ('notes', 'date_visited', 'photo')
        widgets = {
            'date_visited': DateInpu()
        }