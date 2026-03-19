from datetime import timedelta
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone
from tabletop_club_app.models import BoardGame, Rental

User = get_user_model()

class BoardGameModelTests(TestCase):
    def setUp(self):
        # Test data to use in the Board Game Model Tests.
        self.first_test_user = User.objects.create_user(
            username='JSmith54',
            password='testpassword',    
            )
        self.second_test_user = User.objects.create_user(
            username='AWilliams23',
            password='testpassword',
            )
        self.third_test_user = User.objects.create_user(
            username='WDavis79',
            password='testpassword',
        )
        self.test_game = BoardGame.objects.create(
            title='Test Game',
            category=BoardGame.Category.STRATEGY,
            min_players=2,
            max_players=4,
            playtime_minutes=30,
            quantity=2,
            )
        
    def test_board_game_validates_min_players_not_greater_than_max_players(self):
        # Test to verify that the minimum number of players cannot exceed the maximum number of players.
        # The test passes if the expected validation error is raised.
        game = BoardGame(
            title='Invalid Game',
            category=BoardGame.Category.STRATEGY,
            min_players=5, # Minimum players is higher than maximum.
            max_players=4,
            playtime_minutes=60,
            quantity=1,
            )

        with self.assertRaises(ValidationError) as exc:
            game.full_clean()

        self.assertIn(
            "Minimum players cannot be greater than maximum players.", 
            exc.exception.messages,
            )

    def test_available_copies_and_is_available_when_no_rentals(self):
        # Test to verify that a board game with no rentals yet should report that all copies available.
        # The test passes if the game is marked as available while having 2 copies and no active rentals.
        self.assertEqual(self.test_game.active_rentals_count, 0)
        self.assertEqual(self.test_game.available_copies, 2) 
        self.assertTrue(self.test_game.is_available) 

    def test_available_copies_and_is_available_update_with_active_rentals(self):
        # Test to verify that that a game's availability updates correctly when a rental is created.
        # Test passes if available copies decreases from 2 to 1.        
        Rental.objects.create(
            borrower=self.first_test_user,
            board_game=self.test_game,
            date_rented=timezone.localdate(),
            )
        
        self.assertEqual(self.test_game.active_rentals_count, 1)
        self.assertEqual(self.test_game.available_copies, 1)
        self.assertTrue(self.test_game.is_available)

    def test_game_is_unavailable_when_all_games_are_checked_out(self):
        # Test to verify that a game is marked as not available when all of its copies are checked out.
        # Test passes if is_availble returns false after both copies are checked out.
        rented_date = timezone.localdate()
        
        Rental.objects.create(
            borrower=self.first_test_user,
            board_game=self.test_game,
            date_rented=rented_date,
        )

        Rental.objects.create(
            borrower=self.second_test_user,
            board_game=self.test_game,
            date_rented=rented_date,
        )

        self.test_game.refresh_from_db()

        self.assertEqual(self.test_game.active_rentals_count, 2)
        self.assertEqual(self.test_game.available_copies, 0)
        self.assertFalse(self.test_game.is_available)


class RentalModelTests(TestCase):
    def setUp(self):
        # Test data to use in the Rental Model Tests.
        self.first_test_user = User.objects.create_user(
            username='JSmith54',
            password='testpassword',    
            )
        self.second_test_user = User.objects.create_user(
            username='AWilliams23',
            password='testpassword',
            )
        self.third_test_user = User.objects.create_user(
            username='WDavis79',
            password='testpassword',
        )
        self.first_test_game = BoardGame.objects.create(
            title='Test Game',
            category=BoardGame.Category.STRATEGY,
            min_players=2,
            max_players=4,
            playtime_minutes=30,
            quantity=2,
            )
        self.second_test_game = BoardGame.objects.create(
            title='Monopoly',
            category=BoardGame.Category.STRATEGY,
            min_players=2,
            max_players=4,
            playtime_minutes=30,
            quantity=2,
            )
        self.third_test_game = BoardGame.objects.create(
            title='Scrabble',
            category=BoardGame.Category.STRATEGY,
            min_players=2,
            max_players=4,
            playtime_minutes=30,
            quantity=2,
            )
        self.fourth_test_game = BoardGame.objects.create(
            title='Uno',
            category=BoardGame.Category.STRATEGY,
            min_players=2,
            max_players=4,
            playtime_minutes=30,
            quantity=2,
            )
    def test_due_date_is_automatically_set_to_7_days_after_date_rented(self):
        # Test to verify the rule that due date is the rental date + 7 days.
        # Test passes if the due date is 7 days after the rental date.
        rented_date = timezone.localdate()

        rental = Rental.objects.create(
            borrower=self.first_test_user,
            board_game=self.first_test_game,
            date_rented=rented_date,
            )
            
        self.assertEqual(rental.due_date, rented_date + timedelta(days=7))
    
    def test_cannot_rent_more_copies_than_game_quantity(self):
        # Test to verify that a user cannot rent a copy of a game that already has the same number of active rentals as its quantity.
        # Test passes if the expected validation error is raised after a third user attempts to rent a copy of a game with a quantity of 2.
        rented_date = timezone.localdate()

        Rental.objects.create(
            borrower=self.first_test_user,
            board_game=self.first_test_game,
            date_rented=rented_date,
            )
        
        Rental.objects.create(
            borrower=self.second_test_user,
            board_game=self.first_test_game,
            date_rented=rented_date,
            )
        
        rental = Rental(
            borrower=self.third_test_user,
            board_game=self.first_test_game,
            date_rented=rented_date,
            )
        
        with self.assertRaises(ValidationError) as exc:
            rental.full_clean()

        self.assertIn(
            "No copies of this game are currently available.", 
            exc.exception.messages,
            )

    def test_user_cannot_have_more_than_3_concurrent_rentals(self):
        # Test to verify that a user cannot rent a game if they already have 3 active rentals.
        # Test passes if the expected validation error is raised.
        rented_date = timezone.localdate()

        Rental.objects.create(
            borrower=self.first_test_user,
            board_game=self.first_test_game,
            date_rented=rented_date,
            )
        
        Rental.objects.create(
            borrower=self.first_test_user,
            board_game=self.second_test_game,
            date_rented=rented_date,
            )
        
        Rental.objects.create(
            borrower=self.first_test_user,
            board_game=self.third_test_game,
            date_rented=rented_date,
            )
        
        rental = Rental(
            borrower=self.first_test_user,
            board_game=self.fourth_test_game,
            date_rented=rented_date,
            )
        
        with self.assertRaises(ValidationError) as exc:
            rental.full_clean()

        self.assertIn(
            "A user may have at most 3 concurrent rentals.", 
            exc.exception.messages,
            )
    
    def test_user_cannot_rent_same_game_twice_concurrently(self):
        # Test to verify that a user cannot rent a game if they already have an active rental of the same game.
        # Test passes if the the expected validation error is raised.
        rented_date = timezone.localdate()

        Rental.objects.create(
            borrower=self.first_test_user,
            board_game=self.first_test_game,
            date_rented=rented_date,
            )
        
        rental = Rental(
            borrower=self.first_test_user,
            board_game=self.first_test_game,
            date_rented=rented_date,
            )
        
        with self.assertRaises(ValidationError) as exc:
            rental.full_clean()

        self.assertIn(
            "You already have this game rented.", 
            exc.exception.messages,
            )

    def test_is_overdue_returns_true_for_unreturned_rental_past_due_date(self):
        # Test to verify that returning a game past the due date is marked as overdue by returning True.
        # Test passes if the game is marked as overdue.
        rented_date = timezone.localdate() - timedelta(days=10)

        rental = Rental.objects.create(
            borrower=self.first_test_user,
            board_game=self.first_test_game,
            date_rented=rented_date,
            )
            
        self.assertTrue(rental.is_overdue)

