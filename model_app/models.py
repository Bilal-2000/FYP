from PIL import Image
from django.db import models

from fyp.settings import MEDIA_ROOT
from user_app.models import CustomUser


# Create your models here.
class PredictionsModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    prediction_result = models.CharField(max_length=20)
    image = models.ImageField(upload_to="results")
    thumbnail = models.ImageField(upload_to="thumbnails", null=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="history")

    def __str__(self):
        return self.prediction_result

    def save(
            self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        if not self.image:
            self.thumbnail = None
        else:
            thumbnail_size = (100, 100)
            tiny_img = Image.open(self.image)
            tiny_img.thumbnail(thumbnail_size)
            image_path = f"{MEDIA_ROOT}thumbnails/"
            image_name = f"thumbnail_{str(self.image)}"
            tiny_img.save(f"{image_path}{image_name}", format="jpeg")
            self.thumbnail = f"thumbnails/{image_name}"

        super().save(force_insert, force_update, using, update_fields)
