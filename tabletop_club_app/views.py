from django.shortcuts import render

# Create your views here.
def home_admin(request):
    return render(request, 'home_admin.html')

def home_member(request):
    return render(request, 'home_member.html')

def game_catalogue(request):
    return render(request, 'game_catalogue.html')

def members(request):
    return render(request, 'members.html')

def rentals(request):
    return render(request, 'rentals.html')

def my_rentals(request):
    return render(request, 'my_rentals.html')