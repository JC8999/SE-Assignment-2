from django.contrib import admin
from .models import BoardGame, Rental

class BoardGameAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'min_players' ,'max_players', 'playtime_minutes', 'quantity')
    search_fields = ('title', 'category')
    list_filter = ('category',)

class RentalAdmin(admin.ModelAdmin):
    list_display = ('borrower', 'board_game', 'date_rented' ,'due_date')
    search_fields = ('borrower', 'board_game')
    list_filter = ('borrower', 'board_game')

admin.site.register(BoardGame, BoardGameAdmin)
admin.site.register(Rental, RentalAdmin)
