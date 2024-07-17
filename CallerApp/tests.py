from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model

from .models import Contact, Spam

User = get_user_model()

class ContactViewTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(phone='1234567890', password='testpassword', name='Test User')
        self.client.force_authenticate(user=self.user)
        self.contact_data = {'name': 'test', 'phone': '1234567890', 'email': 'test@gmail.com'}
        self.contact = Contact.objects.create(user=self.user, **self.contact_data)
        self.contact_list_url = reverse('add_list_contacts')
    
    def test_get_contacts(self):
        response = self.client.get(self.contact_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'test')

    def test_create_contact(self):
        new_contact_data = {'name': 'test one', 'phone': '1112223330', 'email': 'test.one@gmail.com'}
        response = self.client.post(self.contact_list_url, new_contact_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Contact.objects.count(), 2)
        self.assertEqual(Contact.objects.get(id=response.data['id']).name, 'test one')

    def test_create_contact_duplicate_phone(self):
        response = self.client.post(self.contact_list_url, self.contact_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('This contact is already exists.', response.data['error'])

class SpamViewTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(phone='1234567890', password='testpassword', name='Test User')
        self.client.force_authenticate(user=self.user)
        self.spam_data = {'phone': '1234567890'}
        self.spam = Spam.objects.create(phone=self.spam_data['phone'], report=1)
        self.spam_report_url = reverse('report_spam')

    def test_report_spam(self):
        new_spam_data = {'phone': '0987654321'}
        response = self.client.post(self.spam_report_url, new_spam_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Spam.objects.count(), 2)
        self.assertEqual(Spam.objects.get(phone='0987654321').report, 1)

    def test_report_spam_existing(self):
        response = self.client.post(self.spam_report_url, self.spam_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Spam.objects.count(), 1)
        self.assertEqual(Spam.objects.get(phone='1234567890').report, 2)

class SearchContactByNamePhoneTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(phone='1234567890', password='testpassword', name='Test User')
        self.client.force_authenticate(user=self.user)
        self.contact1 = Contact.objects.create(user=self.user, name='test1', phone='1234567890', email='test.1@gmail.com')
        self.contact2 = Contact.objects.create(user=self.user, name='attest2', phone='0987654321', email='test.2@gmail.com')
        self.spam = Spam.objects.create(phone='1111111111', report=5)
        self.search_url = reverse('search_contact_by_name_phone')

    def test_search_contact_by_name(self):
        response = self.client.get(self.search_url, {'query': 'te', 'type': 'name'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        self.assertEqual(response.data[0]['name'], 'test1')

    def test_search_contact_by_phone(self):
        response = self.client.get(self.search_url, {'query': '0987654321', 'type': 'phone'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['phone'], '0987654321')

    def test_search_spam_by_phone(self):
        response = self.client.get(self.search_url, {'query': '1111111111', 'type': 'phone'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['phone'], '1111111111')
        self.assertEqual(response.data[0]['spam_likelihood'], 5)

    def test_search_no_results(self):
        response = self.client.get(self.search_url, {'query': 'noresult', 'type': 'name'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
