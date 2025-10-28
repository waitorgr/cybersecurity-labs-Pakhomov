from django import forms

HASH_ALGORITHMS = [
    ('sha256', 'SHA-256'),
    ('sha512', 'SHA-512'),
    ('md5', 'MD5'),
]

class SignatureForm(forms.Form):
    first_name = forms.CharField(label="Ім'я", max_length=100)
    last_name = forms.CharField(label="Прізвище", max_length=100)
    birth_date = forms.DateField(label="Дата народження", widget=forms.DateInput(attrs={'type': 'date'}))
    secret_word = forms.CharField(label="Секретне слово", max_length=100)
    document = forms.FileField(label="Документ")
    hash_algorithm = forms.ChoiceField(label="Алгоритм хешування", choices=HASH_ALGORITHMS)

class VerifyForm(forms.Form):
    document = forms.FileField(label="Документ")
    public_n = forms.IntegerField(label="Публічний n")
    public_e = forms.IntegerField(label="Публічний коєфіцієнт e")
    signature = forms.IntegerField(label="Цифровий підпис")
    hash_algorithm = forms.ChoiceField(label="Алгоритм хешування", choices=HASH_ALGORITHMS)
