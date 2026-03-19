from django.test import TestCase
from tabletop_club_app.forms import BoardGameCreationForm

class BoardGameFormTest(TestCase):
    def test_valid_board_game_form(self):
        # Test to verify that the board game creation forms accepts correct data.
        form_data = {
            'title': 'Monopoly',
            'category': 'strategy',
            'min_players': 2,
            'max_players': 6,
            'playtime_minutes': 90,
            'quantity': 5
        }

        form = BoardGameCreationForm(data=form_data)

        self.assertTrue(form.is_valid())

    def test_title_is_required(self):
        # Test to verify that required fields are enforced during creation form.
        form_data = {
            'title': '',
            'category': 'Strategy',
            'min_players': 3,
            'max_players': 4,
            'playtime_minutes': 90,
            'quantity': 5
        }

        form = BoardGameCreationForm(data=form_data)

        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)

    def test_min_players_cannot_exceed_max_players(self):
        # Test to verify that custom validation logic is enforced during creation form.
        form_data = {
            'title': 'Chess',
            'category': 'Strategy',
            'min_players': 5,
            'max_players': 2,
            'playtime_minutes': 30,
            'quantity': 2
        }

        form = BoardGameCreationForm(data=form_data)

        self.assertFalse(form.is_valid())