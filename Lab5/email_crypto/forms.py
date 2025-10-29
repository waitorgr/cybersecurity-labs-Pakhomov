from django import forms

class ComposeForm(forms.Form):
    sender_email = forms.EmailField()
    recipient_email = forms.EmailField()
    subject = forms.CharField(required=False)
    personal_string = forms.CharField(
        label="Персональний ключ (рядок для генерації ключа)",
        widget=forms.PasswordInput,
        help_text="Наприклад: IvanPetrenko1995"
    )
    body = forms.CharField(widget=forms.Textarea)
    attachment = forms.FileField(required=False)

class DecryptForm(forms.Form):
    # For recipient to decrypt
    recipient_email = forms.EmailField()
    personal_string = forms.CharField(widget=forms.PasswordInput)
