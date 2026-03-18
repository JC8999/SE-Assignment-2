from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from tabletop_club_app.models import BoardGame

class AuthenticationTests(TestCase):
    def setUp(self):
        # Test data to use in the authentication tests.
        self.admin = User.objects.create_user(
            username='admin',
            password='testpassword',
            is_staff=True
            )

        self.member = User.objects.create_user(
            username='member',
            password='testpassword',
            is_staff=False
            )

    def test_game_catalogue_requires_login(self):
        # Test to verify that a user that isn't logged in is redirected to login after trying to access the game catalogue page.
        response = self.client.get(reverse('game_catalogue'))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/?next=/game_catalogue/')

    def test_members_page_admin_access(self):
        # Test to verify that the members page is only accessible to admins.
        self.client.login(username='admin', password='testpassword')

        response = self.client.get(reverse('members'))

        self.assertEqual(response.status_code, 200)

    def test_members_page_denies_non_admin_access(self):
        # Test to verify that a non-admin user is denied access to the members page.
        self.client.login(username='member', password='testpassword')

        response = self.client.get(reverse('members'))

        self.assertNotEqual(response.status_code, 200)

class CreateViewTests(TestCase):
    def setUp(self):
        # Test data to use in the create view tests.
        self.admin = User.objects.create_user(
            username='admin',
            password='testpassword',
            is_staff=True
            )
    def test_create_board_game_post(self):
        # Test to verify that submitting valid data creates an object and redirects.
        self.client.login(username='admin', password='testpassword')

        form_data = {
            'title': 'Monopoly',
            'category': 'strategy',
            'min_players': 2,
            'max_players': 6,
            'playtime_minutes': 90,
            'quantity': 5
        }

        response = self.client.post(reverse('create_board_game'), data=form_data)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(BoardGame.objects.count(), 1)

    def test_create_board_game_invalid_post_does_not_create_object(self):
        # Test to verify that submitting invalid data does not create an object and returns the form with errors.
        self.client.login(username='admin', password='testpassword')

        form_data = {
            'title': '', # Invalid title
            'category': 'strategy',
            'min_players': 6, # Invalid min_players
            'max_players': 2,
            'playtime_minutes': 90,
            'quantity': 5
        }

        response = self.client.post(reverse('create_board_game'), data=form_data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(BoardGame.objects.count(), 0)