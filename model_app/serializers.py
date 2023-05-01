from rest_framework import serializers

from model_app.models import PredictionsModel


class PredictionsModelSerializer(serializers.ModelSerializer):
    prediction_result = serializers.CharField(max_length=20)
    image = serializers.ImageField()
    thumbnail = serializers.ImageField(read_only=True)

    class Meta:
        model = PredictionsModel
        fields = ['prediction_result', 'image', "thumbnail"]

    def create(self, validated_data):
        return PredictionsModel.objects.create(**validated_data, user=self.context.get("user"))
