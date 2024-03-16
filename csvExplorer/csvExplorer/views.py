import os
import zipfile
import matplotlib
import numpy as np
import pandas as pd
from scipy.stats import linregress
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from matplotlib import pyplot as plt
matplotlib.use('Agg')
from .forms import UploadFileForm
from .models import UploadedFile

def upload_success(request):
    return HttpResponse("Файл успешно загружен!")

class FileUploadView(FormView):
    template_name = 'upload.html'
    form_class = UploadFileForm
    success_url = reverse_lazy('success_view') 

    def form_valid(self, form):
        uploaded_file = form.cleaned_data['file']
        original_file_name = uploaded_file.name
        file_path = self.save_uploaded_file(uploaded_file)
        graph_paths = []
        
        if zipfile.is_zipfile(file_path):
            graph_paths = self.process_zip_file(file_path, original_file_name)
        else:
            graph_path = self.process_csv_file(file_path, original_file_name)
            if graph_path:
                graph_paths.append(graph_path)
        
        return redirect('success_view') 


    def save_uploaded_file(self, uploaded_file):
        file_path = os.path.join(settings.MEDIA_ROOT, uploaded_file.name)
        with open(file_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)
        return file_path
    
    def process_zip_file(self, file_path, original_file_name):
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
        df = pd.read_csv(file_path)
        numeric_columns = df.select_dtypes(include=['number']).columns.tolist()
        graph_paths = []  # Список для хранения путей к созданным графикам
        
        for column in numeric_columns:
            plt.figure()
            x = np.arange(len(df[column]))
            y = df[column].values
            slope, intercept, r_value, p_value, std_err = linregress(x, y)
            trendline = intercept + slope * x
            plt.plot(x, y, 'o', label='Original Data')
            plt.plot(x, trendline, 'r', label='Trend Line')
            plt.title(f'Graph and Trend Line for {column}')
            plt.xlabel('Index')
            plt.ylabel('Value')
            plt.legend()
            graph_filename = f'{original_file_name}_{column}_graph_with_trendline.png'
            graph_path = os.path.join(settings.MEDIA_ROOT, graph_filename)
            plt.savefig(graph_path)
            plt.close()
            
            relative_graph_path = os.path.relpath(graph_path, settings.MEDIA_ROOT)
            graph_paths.append(relative_graph_path)
            UploadedFile.objects.create(file_name=original_file_name, graph_path=relative_graph_path)
        
        return graph_paths  # Возвращаем список путей к созданным графикам

def success_view(request):
    uploaded_files = UploadedFile.objects.all()
    return render(request, 'success.html', {'uploaded_files': uploaded_files})
