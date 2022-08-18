"""This file contains tests for views."""

from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User

from user.models import Users

MODELS = [Users]


class UserModelViewTests(TestCase):
    '''This class tests the views for :class:`~user.models.Users` objects.'''

    fixtures = ['test_data', ]

    def setUp(self):
        """Instantiate the test client.  Creates a test user."""
        self.client = Client()
        self.test_user = User.objects.create_user(
            'testuser', 'blah@blah.com', 'testpassword')
        self.test_user.is_superuser = True
        self.test_user.is_active = True
        self.test_user.save()
        self.assertEqual(self.test_user.is_superuser, True)
        login = self.client.login(username='testuser', password='testpassword')
        self.failUnless(login, 'Could not log in')

    def tearDown(self):
        """Depopulate created model instances from test database."""
        for model in MODELS:
            for obj in model.objects.all():
                obj.delete()

    def test_user_list(self):
        """This tests the user-listview, ensuring that templates are loaded correctly.  
        This view uses a user with superuser permissions so does not test the permission levels for this view."""

        test_response = self.client.get('/user/')
        self.assertEqual(test_response.status_code, 200)
        self.assertTrue('user_list' in test_response.context)
        self.assertEqual(test_response.context['user_list'][1].pk, 1)
        self.assertEqual(
            test_response.context['user_list'][1].name, u'User Model Instance Name')

    def test_user_view(self):
        """This tests the user-view view, ensuring that templates are loaded correctly.  
        This view uses a user with superuser permissions so does not test the permission levels for this view."""

        test_response = self.client.get('/user/1/')
        self.assertEqual(test_response.status_code, 200)
        self.assertTrue('user' in test_response.context)
        self.assertEqual(test_response.context['user'].pk, 1)
        self.assertEqual(
            test_response.context['user'].name, u'User Model Instance Name')

    def test_user_view_create(self):
        """This tests the user-new view, ensuring that templates are loaded correctly.  
        This view uses a user with superuser permissions so does not test the permission levels for this view."""

        test_response = self.client.post('/user/create/')
        self.assertEqual(test_response.status_code, 200)

    def test_user_view_edit(self):
        """This tests the user-edit view, ensuring that templates are loaded correctly.  
        This view uses a user with superuser permissions so does not test the permission levels for this view."""

        test_response = self.client.put('/user/1/')
        self.assertEqual(test_response.status_code, 200)
        self.assertTrue('user' in test_response.context)
        self.assertEqual(test_response.context['user'].pk, 1)
        self.assertEqual(
            test_response.context['user'].name, u'User Model Instance Name')

        # verifies that a non-existent object returns a 404 error presuming there is no object with pk=2.
        null_response = self.client.put('/user/2/')
        self.assertEqual(null_response.status_code, 404)

    def test_user_view_delete(self):
        """This tests the user-delete view, ensuring that templates are loaded correctly.  
        This view uses a user with superuser permissions so does not test the permission levels for this view."""

        test_response = self.client.delete('/user/1/')
        self.assertEqual(test_response.status_code, 200)
        self.assertTrue('user' in test_response.context)
        self.assertEqual(test_response.context['user'].pk, 1)
        self.assertEqual(
            test_response.context['user'].name, u'User Model Instance Name')

        # verifies that a non-existent object returns a 404 error.
        null_response = self.client.delete('/user/1/')
        self.assertEqual(null_response.status_code, 404)
