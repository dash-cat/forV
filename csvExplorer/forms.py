from django import forms

# Определяем форму для загрузки файла
class UploadFileForm(forms.Form):
    file = forms.FileField()
