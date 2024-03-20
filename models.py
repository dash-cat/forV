from django.db import models

class UploadedFile(models.Model):
    file_name = models.CharField(max_length=255)  # Имя загруженного файла
    graph_paths = models.TextField(blank=True)  # Пути к графикам, сохранённые как строка
    file_size = models.BigIntegerField(default=0)  # Размер файла в байтах
    num_rows = models.IntegerField(default=0)  # Количество строк в файле
    data_types = models.TextField(blank=True)  # Типы данных в файле, сохранённые как строка

    def __str__(self):
        return self.file_name
