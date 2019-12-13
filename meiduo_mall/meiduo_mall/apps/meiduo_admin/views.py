from django.shortcuts import render
from django import http
from rest_framework.views import APIView

# Create your views here.

class MeiDuoAdminView(APIView):

    def get(self, request):
        return http.JsonResponse({'msg': "ok"})

    def post(self, request):
        return http.JsonResponse({'msg': 'OK'})
