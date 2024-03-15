from django.http import HttpResponseRedirect
from django.views.generic.edit import FormView
from .forms import UploadFileForm
from .models import UploadedFile
import pandas as pd

class FileUploadView(FormView):
    template_name = 'upload.html'  # Укажите путь к вашему шаблону
    form_class = UploadFileForm
    success_url = '/'  # URL для перенаправления после успешной загрузки

    def form_valid(self, form):
        # Сохранение файла
        uploaded_file = form.save(commit=False)
        uploaded_file.file = form.cleaned_data['file']
        uploaded_file.save()

        # Чтение и анализ файла с использованием Pandas
        df = pd.read_csv(uploaded_file.file.path)
        # Здесь может быть ваш код для анализа и обработки данных

        return super().form_valid(form)
