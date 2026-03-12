from django.test import TestCase
from django.urls import reverse

class ViewTests(TestCase):
    def test_page_loads(self):
        # Test to verify that the admin home page correctly loads.
        response = self.client.get(reverse('home_admin'))
        self.assertEqual(response.status_code, 200)