from django.db import models, migrations
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from pgvector.django import VectorExtension, VectorField
from langchain_community.docstore.document import Document
# Create your models here.

class Migration(migrations.Migration):
    operations = [
        VectorExtension()
    ]

class User(AbstractUser):
    def get_uploaded_urls(self):
        pass

class UploadedUrl(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    url = models.URLField()
    uploaded_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.url

class Embeddings(models.Model):
    embedding = VectorField(dimensions=1536)
      

