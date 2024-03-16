import os
import zipfile
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import linregress


from .forms import UploadFileForm

def upload_success(request):
    # Возвращаем простое сообщение об успехе без отдельной страницы
    return HttpResponse("Файл успешно загружен!")

class FileUploadView(FormView):
    template_name = 'upload.html'
    form_class = UploadFileForm
    success_url = reverse_lazy('upload_success')  # Перенаправление после успешной загрузки

    def form_valid(self, form):
        uploaded_file = form.cleaned_data['file']
        file_path = self.save_uploaded_file(uploaded_file)

        if zipfile.is_zipfile(file_path):
            self.process_zip_file(file_path)
        else:
            self.process_csv_file(file_path)

        return super().form_valid(form)

    def save_uploaded_file(self, uploaded_file):
        file_path = os.path.join(settings.MEDIA_ROOT, uploaded_file.name)
        with open(file_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)
        return file_path

    def process_csv_file(self, file_path):
        df = pd.read_csv(file_path)
        numeric_columns = df.select_dtypes(include=['number']).columns.tolist()
        
        for column in numeric_columns:
            plt.figure()
            
            # Получаем значения осей x и y для построения графика. Предполагаем, что x - это индекс строки.
            x = np.arange(len(df[column]))
            y = df[column].values
            
            # Вычисляем параметры линейной регрессии
            slope, intercept, r_value, p_value, std_err = linregress(x, y)
            
            # Вычисляем значения y для линии тренда
            trendline = intercept + slope * x
            
            # Строим график значений
            plt.plot(x, y, 'o', label='Оригинальные данные')
            plt.plot(x, trendline, 'r', label='Линия тренда')
            
            plt.title(f'График и линия тренда для столбца {column}')
            plt.xlabel('Индекс')
            plt.ylabel('Значение')
            
            plt.legend()
            
            graph_path = os.path.join(settings.MEDIA_ROOT, f'{column}_graph_with_trendline.png')
            plt.savefig(graph_path)
            plt.close()


def success_view(request):
    # Для отображения созданных графиков, нужно передать пути к ним
    graphs = []  # Список путей к графикам для отображения
    return render(request, 'success.html', {'graphs': graphs})
