from django.http import HttpResponse
from rest_framework.views import APIView


class SuccessView(APIView):

    def get(self, request):
        return HttpResponse(
            "Howdy! looks like the services are up and running fine. \m/"
        )
