from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

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
        response = self.client.get(reverse("game_catalogue"))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/?next=/game_catalogue/")

    def test_members_page_admin_access(self):
        # Test to verify that the members page is only accessible to admins.
        self.client.login(username="admin", password="testpassword")

        response = self.client.get(reverse("members"))

        self.assertEqual(response.status_code, 200)