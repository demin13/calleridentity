from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()

class UserRegisterViewTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('user_registration')
        self.valid_payload = {
            'name': 'Test User',
            'phone': '1234567890',
            'password': 'testpassword',
        }
        self.invalid_payload = {
            'name': '',
            'phone': '',
            'password': '',
        }

    def test_register_user_with_valid_data(self):
        response = self.client.post(self.register_url, self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'User registration success.')
        self.assertTrue(User.objects.filter(phone='1234567890').exists())

    def test_register_user_with_invalid_data(self):
        response = self.client.post(self.register_url, self.invalid_payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

class UserLoginViewTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.login_url = reverse('user_login')
        self.user = User.objects.create_user(
            phone='1234567890',
            password='testpassword',
            name='Test User'
        )
        self.valid_payload = {
            'phone': '1234567890',
            'password': 'testpassword',
        }
        self.invalid_payload = {
            'phone': 'wrongphone',
            'password': 'wrongpassword',
        }

    def test_login_user_with_valid_data(self):
        response = self.client.post(self.login_url, self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['phone'], self.user.phone)

    def test_login_user_with_invalid_data(self):
        response = self.client.post(self.login_url, self.invalid_payload)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Invalid Credentials')
