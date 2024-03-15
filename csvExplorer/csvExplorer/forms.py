from django import forms
from django.views.generic.edit import FormView
import zipfile
import pandas as pd
import os
from django.conf import settings

# Определяем форму для загрузки файла отдельно
class UploadFileForm(forms.Form):
    file = forms.FileField()

class FileUploadView(FormView):
    template_name = 'upload_file.html'

    
    success_url = '/success_url/'  # Укажите URL для перенаправления после успешной загрузки файла

    def form_valid(self, form):
        uploaded_file = form.cleaned_data['file']
        file_path = os.path.join(settings.MEDIA_ROOT, uploaded_file.name)
        
        with open(file_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

        # Обработка файла после сохранения
        try:
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(settings.MEDIA_ROOT)  # Извлечение файлов в директорию для медиа файлов

                for filename in zip_ref.namelist():
                    file_path = os.path.join(settings.MEDIA_ROOT, filename)
                    # Здесь код для анализа и обработки данных из файла
                    # Например, с использованием Pandas
                    df = pd.read_csv(file_path)

                    print("!!!!!", filename)
                    print(df.head())  # Просто пример вывода данных
                    
        except FileNotFoundError:
            print("Файл не найден")
        except zipfile.BadZipFile:
            print("Ошибка при работе с ZIP-файлом")
        
        return super().form_valid(form)
