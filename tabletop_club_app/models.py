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

    def clean(self):
        if self.min_players > self.max_players:
            raise ValidationError("Minimum players cannot be greater than maximum players.")
    
    def __str__(self):
        return self.title
    
class Rental(models.Model):
    borrower = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='rentals')
    board_game = models.ForeignKey(BoardGame, on_delete=models.PROTECT, related_name='rentals')
    date_rented = models.DateField(default=timezone.localdate)
    due_date = models.DateField(editable=False)
    date_returned = models.DateField(blank=True, null=True)

    class Meta:
        ordering = ['-date_rented']

    def save(self, *args, **kwargs):
        # Automatically sets the due date to 7 days after the rental date.
        self.due_date = self.date_rented + timedelta(days=7)
        super().save(*args, **kwargs)
    
    def clean(self):
        if self.date_returned and self.date_returned < self.date_rented:
            raise ValidationError("Date returned cannot be earlier than date rented.")

    def __str__(self):
        return f'{self.borrower} - {self.board_game.title}'