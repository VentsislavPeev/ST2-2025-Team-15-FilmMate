from django.shortcuts import render
from django.http import HttpResponse

def review_list(request):
    return HttpResponse("This will be the list of reviews.")