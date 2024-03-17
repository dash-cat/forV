from audioop import reverse
import os
import zipfile
import matplotlib
import numpy as np
import pandas as pd
from scipy.stats import linregress
from django.conf import settings
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from matplotlib import pyplot as plt
matplotlib.use('Agg')
from .models import UploadedFile
from .forms import UploadFileForm
from django.shortcuts import redirect

def upload_success(request):
    return HttpResponse("Файл успешно загружен!")
 
def file_delete(request, file_id):
    try:
        file_to_delete = UploadedFile.objects.get(id=file_id)
        file_to_delete.delete()
        # После удаления перенаправляем пользователя на нужную страницу
        return HttpResponseRedirect('/success/')
    except UploadedFile.DoesNotExist:
        # Обработка случая, когда файл не найден
        return HttpResponseNotFound('File not found')
    
class FileUploadView(FormView):
    template_name = 'upload.html'
    form_class = UploadFileForm
    success_url = reverse_lazy('success_view') 

    def form_valid(self, form):
        uploaded_file = form.cleaned_data['file']
        original_file_name = uploaded_file.name
        file_path = self.save_uploaded_file(uploaded_file)
        graph_paths = []

        print("A1")

        try:
            if zipfile.is_zipfile(file_path):
                graph_paths = self.process_zip_file(file_path, original_file_name)
            else:
                graph_path = self.process_csv_file(file_path, original_file_name)
                if graph_path:
                    graph_paths.append(graph_path)
        except Exception as e:
            print("exception", e)

        print("A2")
        return redirect('success_view') 

        

    def save_uploaded_file(self, uploaded_file):
        file_path = os.path.join(settings.MEDIA_ROOT, uploaded_file.name)
        with open(file_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)
        return file_path
    
    def  process_zip_file(self, file_path, original_file_name):
        temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp', original_file_name)
        os.makedirs(temp_dir, exist_ok=True)
        
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
            for filename in zip_ref.namelist():
                if filename.endswith('.csv'):
                    self.process_csv_file(os.path.join(temp_dir, filename), original_file_name)
        
        # Очистка временной директории после обработки
        for filename in os.listdir(temp_dir):
            file_path = os.path.join(temp_dir, filename)
            os.remove(file_path)
        os.rmdir(temp_dir)
        return []  # Возвращаем пустой список, если нет графиков


    
    def process_csv_file(self, file_path, original_file_name):
        try:
            df = pd.read_csv(file_path, on_bad_lines='skip')
        except UnicodeDecodeError:
            df = pd.read_csv(file_path, encoding='ISO-8859-1')  # Пробуем с другой кодировкой

        
        # Получаем общие данные о файле
        file_size = os.path.getsize(file_path)
        num_rows = len(df)
        data_types = df.dtypes.to_dict()
        
        # Обрабатываем каждый столбец файла
        relative_graph_paths = []

        for column in df.columns:
            # Проверяем, является ли столбец числовым
            if pd.api.types.is_numeric_dtype(df[column]):
                plt.figure()
                # Используем индекс строки в качестве оси X
                x = np.arange(len(df[column]))
                y = df[column].values

                # Пытаемся вычислить линейную регрессию для числовых данных
                try:
                    slope, intercept, r_value, p_value, std_err = linregress(x, y)
                    trendline = intercept + slope * x

                    plt.plot(x, y, 'o', label='Original Data')
                    plt.plot(x, trendline, 'r', label='Trend Line')
                except ValueError:
                    # Если не получается, просто строим график данных
                    plt.plot(x, y, 'o', label='Original Data')
                
                plt.title(f'{column} (Trend line may not be applicable)')
                plt.xlabel('Index')
                plt.ylabel(column)
                plt.legend()

                graph_filename = f'{original_file_name}_{column}_graph.png'
                graph_path = os.path.join(settings.MEDIA_ROOT, graph_filename)
                plt.savefig(graph_path)
                plt.close()

                relative_graph_path = os.path.relpath(graph_path, settings.MEDIA_ROOT)
                relative_graph_paths.append(relative_graph_path)
            else:
                graph_path = plot_categorical_data(df, column, original_file_name) 
                if graph_path:
                    relative_graph_paths.append(graph_path)

        # Создаем запись в базе данных с информацией о файле и графиках
        uploaded_file = UploadedFile.objects.create(
            file_name=original_file_name,
            graph_paths=','.join(relative_graph_paths),
            file_size=file_size,
            num_rows=num_rows,
            data_types=str(data_types)
        )

        return relative_graph_paths, file_size, num_rows, data_types

def success_view(request):
    uploaded_files = UploadedFile.objects.all()
    if not uploaded_files:  # Если список загруженных файлов пуст
       return HttpResponseRedirect(reverse_lazy('file_upload'))
    return render(request, 'success.html', {'uploaded_files': uploaded_files})

def plot_categorical_data(df, column_name, original_file_name):
    # Проверяем, содержит ли столбец нечисловые данные
    if df[column_name].dtype == object:
        # Подсчитываем количество значений каждой категории
        value_counts = df[column_name].value_counts()
        
        # Создаем столбчатую диаграмму
        plt.figure(figsize=(10, 6))
        try:
            print(df, column_name, original_file_name)
            print("plot")
            value_counts.plot(kind='bar')
        except:
            print("aaaaqaaaaaaaa")
        plt.title(f'Распределение категорий для {column_name}')
        plt.xlabel('Категория')
        plt.ylabel('Количество')
        plt.xticks(rotation=45)
        
        # Сохраняем график
        graph_filename = f'{original_file_name}_{column_name}_category_distribution.png'
        graph_path = os.path.join(settings.MEDIA_ROOT, graph_filename)
        plt.tight_layout()
        plt.savefig(graph_path)
        plt.close()

        return os.path.relpath(graph_path, settings.MEDIA_ROOT)
    else:
        return None