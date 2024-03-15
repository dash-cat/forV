import os
import zipfile
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from matplotlib import pyplot as plt

from .forms import UploadFileForm
from .models import UploadedFile
import pandas as pd

def upload_success(request):
    return HttpResponse("Файл успешно загружен!")

class FileUploadView(FormView):
    template_name = 'upload.html'
    form_class = UploadFileForm
    success_url = reverse_lazy('upload_success')  # URL для перенаправления после успешной загрузки

    def form_valid(self, form):
        uploaded_file = form.cleaned_data['file']
        file_path = os.path.join(settings.MEDIA_ROOT, uploaded_file.name)

        # Проверяем, является ли файл ZIP-архивом
        if zipfile.is_zipfile(file_path):
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                # Создаем временную директорию для распакованных файлов
                temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp')
                os.makedirs(temp_dir, exist_ok=True)
                zip_ref.extractall(temp_dir)

                # Обрабатываем каждый CSV-файл отдельно
                for filename in zip_ref.namelist():
                    if filename.endswith('.csv'):
                        csv_path = os.path.join(temp_dir, filename)
                        df = pd.read_csv(csv_path)
                        # Здесь ваш код для анализа и обработки данных

                # Очищаем временную директорию
                for filename in os.listdir(temp_dir):
                    file_path = os.path.join(temp_dir, filename)
                    os.remove(file_path)
                os.rmdir(temp_dir)
        else:
            # Обработка случая с одним CSV-файлом
            # df = pd.read_csv(file_path)
            # Здесь ваш код для анализа и обработки данных


            return super().form_valid(form)
        
    def plot_histogram(self, data_column):
        plt.figure(figsize=(10, 6))
        plt.hist(data_column, bins=20, color='blue', edgecolor='black')
        plt.title('Распределение значения')
        plt.xlabel('Значение')
        plt.ylabel('Частота')
        plt.savefig(os.path.join(settings.MEDIA_ROOT, 'histogram.png'))  # Сохраняем график в файл
        plt.close()  # Закрываем, чтобы избежать наложения графиков при повторных вызовах
