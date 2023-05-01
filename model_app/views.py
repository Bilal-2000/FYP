import copy

import cv2
import matplotlib.pyplot as plt
import numpy as np
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from fyp.settings import IMG_BREDTH, IMG_HEIGHT
from model_app.apps import ModelConfig
from model_app.models import PredictionsModel
from model_app.serializers import PredictionsModelSerializer

size = 128, 128


# Create your views here.
class PredictView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            img = copy.deepcopy(request.data["image"])
            pic = plt.imread(img.file, format=img.name.split('.')[1])
            model = ModelConfig.predictor
            pic = cv2.resize(pic, (IMG_BREDTH, IMG_HEIGHT))
            pic = np.expand_dims(pic, axis=0)
            classes = model.predict(pic)
            output_string = f"Organic" if classes[0][0] > classes[0][1] else "Recyclable"
            temp = request.data
            temp['prediction_result'] = output_string
            serializer = PredictionsModelSerializer(data=temp, context={"user": self.request.user})
            if serializer.is_valid():
                serializer.save()
                return Response({f"The waste picture you provided is {output_string} and can be dumped"}
                                if output_string == "Organic"
                                else {f"The waste picture you provided is {output_string} and should be recycled"},
                                status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                data={"error": serializer.errors})

        except Exception as e:
            return Response({'Error': str(e)})


class HistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            queryset = PredictionsModel.objects.filter(user=self.request.user)
            if not queryset:
                return Response({"Error": "No records for the current user"}, status=status.HTTP_400_BAD_REQUEST)
            serializer = PredictionsModelSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as err:
            return Response(str(err), status=status.HTTP_400_BAD_REQUEST)
