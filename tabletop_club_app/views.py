from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.shortcuts import render
from django.urls import reverse_lazy
from .models import BoardGame, Rental

# Create your views here.
def home_admin(request):
    return render(request, 'home_admin.html')

def home_member(request):
    return render(request, 'home_member.html')

def game_catalogue(request):
    game_list = BoardGame.objects.all().order_by('title')
    return render(request, 'game_catalogue.html', {'games': game_list})

def members(request):
    member_list = User.objects.filter(is_staff=False)
    return render(request, 'members.html', {'members': member_list})

def rentals(request):
    rental_list = Rental.objects.all().order_by('date_rented')
    return render(request, 'rentals.html', {'rentals': rental_list})

def my_rentals(request):
    return render(request, 'my_rentals.html')

class CustomLoginView(LoginView):
    template_name="login.html"

    def get_success_url(self):
        user=self.request.user

        if user.is_staff:
            return reverse_lazy('home_admin')
        
        return reverse_lazy('home_member')