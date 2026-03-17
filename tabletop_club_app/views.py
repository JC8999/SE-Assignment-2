from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.core.exceptions import ValidationError
from django.db.models.deletion import ProtectedError
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from .forms import MemberCreationForm, BoardGameCreationForm, MemberEditForm
from .models import BoardGame, Rental

# Custom login view used to automatically redirect to the appropriate home page depending on which user role is authenticated.
class CustomLoginView(LoginView):
    template_name='login.html'

    def get_success_url(self):
        user=self.request.user

        # Redirects to the admin homepage if the user is an admin.
        if user.is_staff:
            return reverse_lazy('home_admin')
        
        # Redirects to the member homepage if the user is not an admin.
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

    rental_list = Rental.objects.filter(borrower=request.user).select_related('board_game')
    return render(request, 'my_rentals.html', {'rentals': rental_list})

# ====== Form Views ====== #
# Create Member
@staff_member_required
def create_member(request):
    if request.method == 'POST':
        form = MemberCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Member created successfully.')
            return redirect('members')
    else:
        form = MemberCreationForm()

    return render(request, 'create_member.html', {'form': form})

# Create Board Game
@staff_member_required
def create_board_game(request):
    if request.method == 'POST':
        form = BoardGameCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Board Game created successfully.')
            return redirect('game_catalogue')
    else:
        form = BoardGameCreationForm()

    return render(request, 'create_board_game.html', {'form': form})

# Edit Member
@staff_member_required
def edit_member(request, pk):
    member = get_object_or_404(User, pk=pk)

    if request.method == 'POST':
        form = MemberEditForm(request.POST, instance=member)
        if form.is_valid():
            form.save()
            messages.success(request, 'Member details updated successfully.')
            return redirect('members')
    else:
        form = MemberEditForm(instance=member)

    return render(request, 'edit_member.html', {'form': form, 'member': member})

# Edit Board Game
@staff_member_required
def edit_board_game(request, pk):
    game = get_object_or_404(BoardGame, pk=pk)

    if request.method == 'POST':
        form = BoardGameCreationForm(request.POST, instance=game)
        if form.is_valid():
            form.save()
            messages.success(request, 'Board Game details updated successfully.')
            return redirect('game_catalogue')
    
    else:
        form = BoardGameCreationForm(instance=game)

    return render(request, 'edit_board_game.html', {'form': form, 'game': game})

# Delete Member
@staff_member_required
def delete_member(request, pk):
    member = get_object_or_404(User, pk=pk)

    if request.method == 'POST':
        try:
            member.delete()
            messages.success(request, 'Member deleted successfully.')
            return redirect('members')
        except ProtectedError:
            messages.error(
                request,
                'This member cannot be deleted because they have active or related rentals.'
            )
            return redirect('members')

    return render(request, 'delete_member.html', {'member': member})

# Delete Board Game
@staff_member_required
def delete_board_game(request, pk):
    game = get_object_or_404(BoardGame, pk=pk)

    if request.method == 'POST':
        try:
            game.delete()
            messages.success(request, 'Board game deleted successfully.')
            return redirect('game_catalogue')
        except ProtectedError:
            messages.error(
                request,
                'This board game cannot be deleted because it has active rentals.'
            )
            return redirect('game_catalogue')

    return render(request, 'delete_board_game.html', {'game': game})

# ====== Rental Views ======
# Rent Board Game
@login_required
def rent_game(request, pk):
    # Prevents admins from renting a game
    if request.user.is_staff:
        messages.error(request, 'Admins cannot rent board games.')
        return redirect('game_catalogue')

    game = get_object_or_404(BoardGame, pk=pk)

    if request.method == 'POST':
        rental = Rental(
            borrower=request.user,
            board_game=game
        )

        try:
            rental.full_clean() # Runs to ensure rental rules are enforced
            rental.save()
            messages.success(request, f'You have rented "{game.title}".')
            return redirect('my_rentals')
        except ValidationError as e: # Used to display error messages from the rental rules
            for error in e.messages:
                messages.error(request, error)
            return redirect('game_catalogue')

    return redirect('game_catalogue')

# Return Board Game
@login_required
def return_game(request, pk):
    rental = get_object_or_404(Rental, pk=pk)

    # Members can only return their own rentals
    if rental.borrower != request.user:
        messages.error(request, 'You cannot return this rental.')
        return redirect('my_rentals')

    if request.method == 'POST':
        game_title = rental.board_game.title
        rental.delete()
        messages.success(request, f'You returned "{game_title}".')
        return redirect('my_rentals')

    return render(request, 'return_game.html', {'rental': rental})