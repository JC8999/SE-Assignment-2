from datetime import timedelta
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

class BoardGame(models.Model):
    class Category(models.TextChoices):
        STRATEGY = 'strategy', 'Strategy'
        PARTY = 'party', 'Party'

    title = models.CharField(max_length=100, unique=True,)
    category = models.CharField(max_length=20, choices=Category.choices)
    min_players = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    max_players = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    playtime_minutes = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])

    class Meta:
        ordering = ['title']

    @property
    def active_rentals_count(self):
        # Counts the number of rentals of a game that have not been returned. Used to calculate the available copies remaining.
        return self.rentals.count()
    
    @property
    def available_copies(self):
        # Calculates the available copies of a game remaining. Used to determine if a game is available to rent.
        return self.quantity - self.active_rentals_count

    @property
    def is_available(self):
        # Determines if a game is available. Used to disable the "rent game" button while there are no copies remaining.
        return self.available_copies > 0

    def clean(self):
        # Enforces rule that minimum players can't be greater than maximum players.
        if self.min_players > self.max_players:
            raise ValidationError("Minimum players cannot be greater than maximum players.")
    
    def __str__(self):
        return self.title
    
class Rental(models.Model):
    borrower = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='rentals')
    board_game = models.ForeignKey(BoardGame, on_delete=models.PROTECT, related_name='rentals')
    date_rented = models.DateField(default=timezone.localdate)
    due_date = models.DateField(editable=False)

    class Meta:
        ordering = ['-date_rented']

    @property
    def is_overdue(self):
        # Determines if a board game is overdue.
        return timezone.localdate() > self.due_date

    def save(self, *args, **kwargs):
        # Automatically sets the due date to 7 days after the rental date.
        self.due_date = self.date_rented + timedelta(days=7)
        super().save(*args, **kwargs)
    
    def clean(self):
        #  Enforces rule that a rental can't be created if no copies of the game are available.
        active_rentals_for_game = Rental.objects.filter(board_game=self.board_game)
            # Checks to see if the object already exists to prevent counting it as another active rental during editing.
        if self.pk:
            active_rentals_for_game = active_rentals_for_game.exclude(pk=self.pk)
        
        if active_rentals_for_game.count() >= self.board_game.quantity:
            raise ValidationError("No copies of this game are currently available.")
        
        # Enforces rule that a user cannot have more than 3 concurrent rentals.
        active_rentals_for_user = Rental.objects.filter(borrower=self.borrower)
            # Checks to see if the object already exists to prevent counting it as another active rental during editing.
        if self.pk:
            active_rentals_for_user = active_rentals_for_user.exclude(pk=self.pk)

        if active_rentals_for_user.count() >= 3:
            raise ValidationError("A user may have at most 3 concurrent rentals.")

        # Enforces rule that a user cannot rent two copies of the same game concurrently.    
        duplicate_rental = Rental.objects.filter(
            borrower=self.borrower,
            board_game=self.board_game,
            )
        if self.pk:
            duplicate_rental = duplicate_rental.exclude(pk=self.pk)
        
        if duplicate_rental.exists():
            raise ValidationError("You already have this game rented.")

    def __str__(self):
        return f'{self.borrower} - {self.board_game.title}'