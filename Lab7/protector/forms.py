from django import forms

from django import forms

class UploadForm(forms.Form):
    file = forms.FileField(label="Файл для захисту", required=False)
    text = forms.CharField(widget=forms.Textarea, label="Текст для шифрування", required=False)
    cover_image = forms.ImageField(label="Контейнер (PNG/BMP) для стеганографії")
    password = forms.CharField(widget=forms.PasswordInput, required=False, help_text="Пароль для AES ключа")
    
    def clean(self):
        cleaned_data = super().clean()
        file = cleaned_data.get("file")
        text = cleaned_data.get("text")
        if not file and not text:
            raise forms.ValidationError("Потрібно завантажити файл або ввести текст")
        return cleaned_data
