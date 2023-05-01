from keras.models import load_model
from django.apps import AppConfig
from django.conf import settings


class ModelConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'model_app'
    predictor = load_model(f"{settings.BASE_DIR}/fyp/static/Acc80.h5")
    