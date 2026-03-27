from django.db import models
from pgvector.django import VectorField
# Create your models here.

class Document(models.Model):
    title = models.CharField(max_length=255)
    sharepoint_id = models.CharField(max_length=255, unique=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class DocumentChunk(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='chunks')
    page_number = models.IntegerField(default=1)

    content = models.TextField()
    embedding = VectorField(dimensions=384)

    def __str__(self):
        return f"Pagina {self.page_number} de {self.document.title}"