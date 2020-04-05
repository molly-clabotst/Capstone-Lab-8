from django.test import TestCase
from django.urls import reverse

from .models import Place

# Create your tests here.

class TestHomePageIsEmptyList(TestCase):

    def test_load_home_page_shows_empty_list(self):
        response = self.client.get(reverse('place_list'))
        self.assertTemplateUsed(response, 'travel_wishlist/wishlist.html')
        self.assertFalse(response.context['places'])
        self.assertContains(response, 'You have no places in your wishlist')

class TestWishList(TestCase):

    fixtures = ['test_places']

    def test_view_wislist_contains_not_visited_places(self):
        response = self.client.get(reverse('place_list'))
        self.assertTemplateUsed(response, 'travel_wishlist/wishlist.html')

        self.assertContains(response, 'Tokyo')
        self.assertContains(response, 'New York')
        self.assertNotContains(response,'San Francisco')
        self.assertNotContains(response, 'Moab')

class TestVisitedIsEmptyList(TestCase):

    def test_no_places_visited_shows_message(self):
        response = self.client.get(reverse('places_visited'))
        self.assertTemplateUsed(response, 'travel_wishlist/visited.html')
        self.assertFalse(response.context['visited'])
        self.assertContains(response, 'You have not visited any places yet.')

class TestVisitedList(TestCase):

    fixtures = ['test_places']

    def test_view_visited_contains_visited_only(self):
        response = self.client.get(reverse('places_visited'))
        self.assertTemplateUsed(response, 'travel_wishlist/visited.html')
        
        self.assertNotContains(response, 'Tokyo')
        self.assertNotContains(response,'New York')
        self.assertContains(response, 'San Francisco')
        self.assertContains(response, 'Moab')

