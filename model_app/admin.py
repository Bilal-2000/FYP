from django.contrib import admin

from model_app.models import PredictionsModel


# Register your models here.
class ImageAdmin(admin.ModelAdmin):
    list_display = ['prediction_result', 'image']


admin.site.register(PredictionsModel, ImageAdmin)
