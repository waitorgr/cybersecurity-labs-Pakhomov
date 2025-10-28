# --------------------
# File: steg/forms.py
# --------------------
from django import forms


class HideForm(forms.Form):
    image = forms.ImageField()
    message = forms.CharField(widget=forms.Textarea, required=True)
    key = forms.CharField(required=False, help_text='Optional key to encrypt the payload (symmetric XOR)')
    channels = forms.MultipleChoiceField(choices=[('0','R'),('1','G'),('2','B')], initial=['0','1','2'], widget=forms.CheckboxSelectMultiple)


class ExtractForm(forms.Form):
    image = forms.ImageField()
    key = forms.CharField(required=False)
    channels = forms.MultipleChoiceField(choices=[('0','R'),('1','G'),('2','B')], initial=['0','1','2'], widget=forms.CheckboxSelectMultiple)