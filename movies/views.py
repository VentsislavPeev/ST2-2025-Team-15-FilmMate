from django.shortcuts import render
from django.http import HttpResponse

def movie_list(request):
    return HttpResponse("This will be the list of movies.")

