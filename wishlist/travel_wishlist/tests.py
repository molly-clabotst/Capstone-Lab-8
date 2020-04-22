import tempfile
import filecmp
import os 

from django.test import TestCase
from django.urls import reverse
from django.test import override_settings

from django.contrib.auth.models import User
from .models import Place

from PIL import Image 

# Create your tests here.

class TestHomePageIsEmptyList(TestCase):
    
    fixtures = ['test_users']

    def setUp(self):
        user = User.objects.get(pk=1)
        self.client.force_login(user)

    def test_load_home_page_shows_empty_list(self):
        response = self.client.get(reverse('place_list'))
        self.assertTemplateUsed(response, 'travel_wishlist/wishlist.html')
        self.assertFalse(response.context['places'])
        self.assertContains(response, 'You have no places in your wishlist')

    def test_load_visited_page_shows_empty_list(self):
        response = self.client.get(reverse('places_visited'))
        self.assertTemplateUsed(response, 'travel_wishlist/visited.html')
        self.assertEquals(0, len(response.context['visited']))


class TestWishList(TestCase):

    fixtures = ['test_places', 'test_users']

    def setUp(self):
        self.user = User.objects.get(pk=1)
        self.client.force_login(self.user)

    def test_view_wislist_contains_not_visited_places(self):
        response = self.client.get(reverse('place_list'))
        self.assertTemplateUsed(response, 'travel_wishlist/wishlist.html')

        # What data was sent to the template
        data_rendered = list(response.context['places'])
        # What data is in the database? Get all of the items for this user where visited = false
        data_expectd = list(Place.objects.filter(user=self.user).filter(visited=False))

        self.assertCountEqual(data_rendered, data_rendered)



class TestAddNewPlace(TestCase):

    fixtures = ['test_users']

    def setUp(self):
        user = User.objects.get(pk=1)
        self.client.force_login(user)

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

        # Add a new place, assert it used the right template and assert that there are two places on the list now
        response = self.client.post(reverse('place_list'), {'name': 'Yosemite', 'visited': False }, follow=True)
        self.assertTemplateUsed(response, 'travel_wishlist/wishlist.html')
        response_places = response.context['places']
        self.assertEqual(len(response_places), 2)

        # This data should be in the database will throw error if not
        place_in_database = Place.objects.get(name="Yosemite", visited=False)
        place_in_database = Place.objects.get(name="Tokyo", visited=False)

        places_in_database = Place.objects.all()

        # Making sure everything used in the template is in the database
        self.assertCountEqual(list(places_in_database), list(response_places))

    def test_add_new_visited_place_to_wishlist(self):

        response = self.client.post(reverse('place_list'), { 'name': 'Tokyo', 'visited': True }, follow=True)
        self.assertTemplateUsed(response, 'travel_wishlist/wishlist.html')
        response_places = response.context['places']
        self.assertEqual(len(response_places), 0)
        place_in_database = Place.objects.get(name="Tokyo", visited=True)


class TestMarkPlaceAsVisited(TestCase):

    fixtures = ['test_places', 'test_users']

    def setUp(self):
        self.user = User.objects.get(pk=1)
        self.client.force_login(self.user)


    def test_mark_unvisited_place_as_visited(self):

        response = self.client.post(reverse('place_was_visited', args=(2,)), follow=True)
        # Assert redirected to place list
        self.assertTemplateUsed(response, 'travel_wishlist/wishlist.html')

        place = Place.objects.get(pk=2)
        self.assertTrue(place.visited)


    def test_mark_non_existent_place_as_visited_returns_404(self):
        response = self.client.post(reverse('place_was_visited', args=(200,)), follow=True)
        self.assertEqual(404, response.status_code)


    def test_visit_someone_else_place_not_authorized(self):
        response = self.client.post(reverse('place_was_visited', args=(5,)), follow=True)
        self.assertEqual(403, response.status_code)  # 403 Forbidden


class TestDeletePlace(TestCase):

    fixtures = ['test_places', 'test_users']

    def setUp(self):
        user = User.objects.first()
        self.client.force_login(user)


    def test_delete_own_place(self):
        response = self.client.post(reverse('delete_place', args=(2,)), follow=True)
        place_2 = Place.objects.filter(pk=2).first()
        self.assertIsNone(place_2)   # place is deleted


    def test_delete_someone_else_place_not_auth(self):
        response = self.client.post(reverse('delete_place',  args=(5,)), follow=True)
        self.assertEqual(403, response.status_code)
        place_5 = Place.objects.get(pk=5)
        self.assertIsNotNone(place_5)    # place still in database


class TestPlaceDetail(TestCase):

    fixtures = ['test_places', 'test_users']

    def setUp(self):
        user = User.objects.get(pk=1)
        self.client.force_login(user)


    def test_modify_someone_else_place_details_not_authorized(self):
        response = self.client.post(reverse('place_details', kwargs={'place_pk':5}), {'notes':'awesome'}, follow=True)
        self.assertEqual(403, response.status_code) 
        

    def test_place_detail(self):
        place_1 = Place.objects.get(pk=1)

        response = self.client.get(reverse('place_details', kwargs={'place_pk':1} ))

        self.assertTemplateUsed(response, 'travel_wishlist/place_details.html')

        data_rendered = response.context['place']

        self.assertEqual(data_rendered, place_1)   
        self.assertContains(response, 'Tokyo') 
        self.assertContains(response, 'cool')  
        self.assertContains(response, '2014-01-01') 


    def test_modify_notes(self):

        response = self.client.post(reverse('place_details', kwargs={'place_pk':1}), {'notes':'awesome'}, follow=True)

        updated_place_1 = Place.objects.get(pk=1)

        self.assertEqual('awesome', updated_place_1.notes)
        self.assertEqual(response.context['place'], updated_place_1)
        self.assertTemplateUsed(response, 'travel_wishlist/place_details.html')
        self.assertNotContains(response, 'cool') 
        self.assertContains(response, 'awesome')
       

    def test_add_notes(self):

        response = self.client.post(reverse('place_details', kwargs={'place_pk':4}), {'notes':'yay'}, follow=True)

        updated_place_4 = Place.objects.get(pk=4)

        # Making sure the notes are added, the right place is updated,
        # the right template is updated and that what is in the response
        # is in the template
        self.assertEqual('yay', updated_place_4.notes)
        self.assertEqual(response.context['place'], updated_place_4)
        self.assertTemplateUsed(response, 'travel_wishlist/place_details.html')
        self.assertContains(response, 'yay')
       

    def test_add_date_visited(self):

        date_visited = '2014-01-01'

        response = self.client.post(reverse('place_details', kwargs={'place_pk':4}), {'date_visited': date_visited}, follow=True)

        updated_place_4 = Place.objects.get(pk=4)

        # Making sure the date is in the right format, the place is created, 
        # the right template is used and that what is on the template is what 
        # is in the response.
        self.assertEqual(updated_place_4.date_visited.isoformat(), date_visited) 
        self.assertEqual(response.context['place'], updated_place_4)
        self.assertTemplateUsed(response, 'travel_wishlist/place_details.html')
        self.assertContains(response, date_visited)
       


class TestImageUpload(TestCase):

    fixtures = ['test_users', 'test_places']

    def setUp(self):
        user = User.objects.get(pk=1)
        self.client.force_login(user)
        self.MEDIA_ROOT = tempfile.mkdtemp()
        

    def tearDown(self):
        print('todo delete temp directory, temp image')


    def create_temp_image_file(self):
        handle, tmp_img_file = tempfile.mkstemp(suffix='.jpg')
        img = Image.new('RGB', (10, 10) )
        img.save(tmp_img_file, format='JPEG')
        return tmp_img_file


    def test_upload_new_image_for_own_place(self):
        
        img_file_path = self.create_temp_image_file()


        with self.settings(MEDIA_ROOT=self.MEDIA_ROOT):
        
            with open(img_file_path, 'rb') as img_file:
                resp = self.client.post(reverse('place_details', kwargs={'place_pk': 1} ), {'photo': img_file }, follow=True)
                
                self.assertEqual(200, resp.status_code)

                place_1 = Place.objects.get(pk=1)
                img_file_name = os.path.basename(img_file_path)
                expected_uploaded_file_path = os.path.join(self.MEDIA_ROOT, 'use_images', img_file_name)

                # Making sure the photo and file path exist. Making sure that it is the 
                # same as what is expected.
                self.assertTrue(os.path.exists(expected_uploaded_file_path))
                self.assertIsNotNone(place_1.photo)
                self.assertTrue(filecmp.cmp( img_file_path,  expected_uploaded_file_path ))


    def test_change_image_for_own_place_expect_old_deleted(self):
        
        first_img_file_path = self.create_temp_image_file()
        second_img_file_path = self.create_temp_image_file()

        with self.settings(MEDIA_ROOT=self.MEDIA_ROOT):
        
            with open(first_img_file_path, 'rb') as first_img_file:

                resp = self.client.post(reverse('place_details', kwargs={'place_pk': 1} ), {'photo': first_img_file }, follow=True)

                place_1 = Place.objects.get(pk=1)

                first_uploaded_image = place_1.photo.name

                with open(second_img_file_path, 'rb') as second_img_file:
                    resp = self.client.post(reverse('place_details', kwargs={'place_pk':1}), {'photo': second_img_file}, follow=True)

                    # first file should not exist 
                    # second file should exist 

                    place_1 = Place.objects.get(pk=1)

                    second_uploaded_image = place_1.photo.name

                    first_path = os.path.join(self.MEDIA_ROOT, first_uploaded_image)
                    second_path = os.path.join(self.MEDIA_ROOT, second_uploaded_image)

                    self.assertFalse(os.path.exists(first_path))
                    self.assertTrue(os.path.exists(second_path))


    def test_upload_image_for_someone_else_place(self):

        with self.settings(MEDIA_ROOT=self.MEDIA_ROOT):
  
            img_file = self.create_temp_image_file()
            with open(img_file, 'rb') as image:
                resp = self.client.post(reverse('place_details', kwargs={'place_pk': 5} ), {'photo': image }, follow=True)
                self.assertEqual(403, resp.status_code)

                place_5 = Place.objects.get(pk=5)
                self.assertFalse(place_5.photo)  


    def test_delete_place_with_image_image_deleted(self):
        
        img_file_path = self.create_temp_image_file()

        with self.settings(MEDIA_ROOT=self.MEDIA_ROOT):
        
            with open(img_file_path, 'rb') as img_file:
                resp = self.client.post(reverse('place_details', kwargs={'place_pk': 1} ), {'photo': img_file }, follow=True)
                
                self.assertEqual(200, resp.status_code)

                place_1 = Place.objects.get(pk=1)
                img_file_name = os.path.basename(img_file_path)
                
                uploaded_file_path = os.path.join(self.MEDIA_ROOT, 'user_images', img_file_name)

                place_1 = Place.objects.get(pk=1)
                place_1.delete()

                self.assertFalse(os.path.exists(uploaded_file_path))
               