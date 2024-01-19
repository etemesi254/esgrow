from django.http import HttpResponse
from django.shortcuts import render
from rest_framework import serializers

from esgrow_backend.models import User


# Create your views here.

def index(request):
    return HttpResponse("Hello, world. You're at the api index.")
