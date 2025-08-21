from django.db import models
import uuid

class PublicProductLink(models.Model):
    product_id = models.CharField(max_length=255)
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    product_data = models.JSONField(null=True, blank=True)

