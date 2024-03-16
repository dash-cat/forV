from django.db import models

class UploadedFile(models.Model):
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    file_name = models.CharField(max_length=255, default='')
    graph_path = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.file_name
