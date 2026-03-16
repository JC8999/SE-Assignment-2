from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from .forms import MemberCreationForm, BoardGameCreationForm
from .models import BoardGame, Rental

# Create your views here.
class CustomLoginView(LoginView):
    template_name="login.html"

    def get_success_url(self):
        user=self.request.user

        if user.is_staff:
            return reverse_lazy('home_admin')
        
        return reverse_lazy('home_member')

# ====== Views ====== #
@login_required
def home_admin(request):
    if not request.user.is_staff: # Checks if user is an admin and redirects them to the appropriate home page if they are not.
        return redirect('home_member')
    return render(request, 'home_admin.html')

@login_required
def home_member(request):
    if request.user.is_staff: # Checks if user is an admin and redirects them to the appropriate home page if they are.
        return redirect('home_admin')
    return render(request, 'home_member.html')

@login_required
def game_catalogue(request):
    game_list = BoardGame.objects.all().order_by('title')
    return render(request, 'game_catalogue.html', {'games': game_list})

@login_required
def members(request):
    if not request.user.is_staff: # Checks if user is an admin and redirects them to the appropriate home page if they are not.
        return redirect('home_member')

    member_list = User.objects.filter(is_staff=False)
    return render(request, 'members.html', {'members': member_list})

@login_required
def rentals(request):
    if not request.user.is_staff: # Checks if user is an admin and redirects them to the appropriate home page if they are not.
        return redirect('home_member')

    rental_list = Rental.objects.all().order_by('date_rented')
    return render(request, 'rentals.html', {'rentals': rental_list})

@login_required
def my_rentals(request):
    if request.user.is_staff: # Checks if user is an admin and redirects them to the appropriate home page if they are.
        return redirect('home_admin')

    return render(request, 'my_rentals.html')

# ====== Form Views ====== #
@staff_member_required
def create_member(request):
    if request.method == 'POST':
        form = MemberCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('members')
    else:
        form = MemberCreationForm()

    return render(request, 'create_member.html', {'form': form})
    
@staff_member_required
def create_board_game(request):
    if request.method == "POST":
        form = BoardGameCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("game_catalogue")
    else:
        form = BoardGameCreationForm()

    return render(request, "create_board_game.html", {"form": form})