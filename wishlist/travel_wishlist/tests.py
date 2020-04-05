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

class TestAddNewPlace(TestCase):

    def test_add_new_unvisited_place_to_wishlist(self):
        
        response = self.client.post(reverse('place_list'), {'name':'Tokyo', 'visited': False }, follow=True)

        # Check correct template was used
        self.assertTemplateUsed(response, 'travel_wishlist/wishlist.html')

        # What data was used to populate the template?
        response_places = response.context['places']
        # Should be 1 item
        self.assertEqual(len(response_places), 1)
        tokyo_response = response_places[0]

        # Expect this data to be in the databse. Use get()to get data with
        # the values expected. Will throw an exception if no data, or more than
        # one row, matches. Remember throwing an exception will cause this test to fail
        tokyo_in_database = Place.objects.get(name='Tokyo', visited = False)

        # Is the data used to render the template, the same as the data in the database?
        self.assertEqual(tokyo_response, tokyo_in_database)

class TestVisitedPlace(TestCase):
    
    fixtures = ['test_places']

    def test_visit_place(self):

        # visit place pk = 2, New York
        response = self.client.post(reverse('place_was_visited', args=(2,) ), follow=True)

        # Check correct template was used
        self.assertTemplateUsed(response, 'travel_wishlist/wishlist.html')

        # No New York in the response
        self.assertNotContains(response, 'New York')

        # Is New York visited?
        new_york = Place.objects.get(pk=2)
        self.assertTrue(new_york.visited)

    def test_visit_non_existent_place(self):

        # visit place pk = 200, does not exist
        response = self.client.post(reverse('place_was_visited', args=(200,) ), follow=True)
        self.assertEqual(response.status_code, 404) 