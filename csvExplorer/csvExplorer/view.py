from django.http import HttpResponseRedirect
from django.shortcuts import render
from .forms import UploadFileForm
from .models import UploadedFile
import pandas as pd

def file_upload_view(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            new_file = UploadedFile(file=request.FILES['file'])
            new_file.save()
            # Чтение и анализ файла с использованием Pandas
            df = pd.read_csv(new_file.file.path)
            # Здесь может быть анализ и визуализация
            return HttpResponseRedirect('/')
    else:
        form = UploadFileForm()
    return render(request, 'upload.html', {'form': form})
