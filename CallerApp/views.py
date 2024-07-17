from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model

from .models import Contact, Spam
from .serializers import ContactSerializer, SpamSerializer, SpamInputSerializer
from CallerApp.utility.handler import Validator, handle_exceptions

User = get_user_model()

class ContactView(APIView):

    @staticmethod
    @handle_exceptions
    def get(request, id=None):
        contacts = Contact.objects.filter(user=request.user)
        serializer = ContactSerializer(contacts, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
    
    @staticmethod
    @handle_exceptions
    def post(request):
        serializer = ContactSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        return Response(data={"error": Validator.TrimSerializerError(serializer.errors)}, 
                        status=status.HTTP_400_BAD_REQUEST)
    
class SpamView(APIView):

    @staticmethod
    @handle_exceptions
    def post(request):
        serializer = SpamInputSerializer(data=request.data)
        if serializer.is_valid():
            phone = serializer.validated_data.get('phone')
            spam, created = Spam.objects.get_or_create(phone=phone)
            spam.report += 1
            spam.save()
            return Response(data={"message": "This phone number has been successfully reported as spam."},
                            status=status.HTTP_200_OK)
        return Response(data={"error": Validator.TrimSerializerError(serializer.errors)}, 
                        status=status.HTTP_400_BAD_REQUEST)
   
    
class SearchContactByNamePhone(APIView):

    @handle_exceptions
    def get(self, request):
        query = request.GET.get('query', '')
        search_type = request.GET.get('type')
        results = []
        
        if search_type == 'name':
            results = self.search_by_name(query)
        elif search_type == 'phone':
            results = self.search_by_phone(query)
        
        return Response(data=results, status=status.HTTP_200_OK)

    def search_by_name(self, query):
        contacts = Contact.objects.filter(name__icontains=query)
        users = User.objects.filter(name__icontains=query)
        
        contact_results = self.format_contacts(contacts)
        user_results = self.format_users(users)
        
        sorted_results = sorted(contact_results + user_results, key=lambda x: (not x['name'].startswith(query), x['name']))
        
        return sorted_results
    
    def search_by_phone(self, query):
        contacts = Contact.objects.filter(phone=query)
        users = User.objects.filter(phone=query)
        
        contact_results = self.format_contacts(contacts)
        user_results = self.format_users(users)

        result = contact_results + user_results

        if not result:
            spam_report = Spam.objects.filter(phone=query).first()
            if spam_report:
                result.append({
                    'name': None,
                    'phone': spam_report.phone,
                    'spam_likelihood': spam_report.report,
                    'email': None
                })
        
        return result

    def format_contacts(self, contacts):
        results = []
        for contact in contacts:
            spam_likelihood = self.get_spam_likelihood(contact.phone)
            results.append({
                'name': contact.name,
                'phone': contact.phone,
                'spam_likelihood': spam_likelihood,
                'email': contact.email if contact.user == self.request.user else None
            })
        return results

    def format_users(self, users):
        results = []
        for user in users:
            spam_likelihood = self.get_spam_likelihood(user.phone)
            results.append({
                'name': user.name,
                'phone': user.phone,
                'spam_likelihood': spam_likelihood,
                'email': user.email if user in self.request.user.contacts.all() else None
            })
        return results
    
    def get_spam_likelihood(self, phone):
        spam_report = Spam.objects.filter(phone=phone).first()
        if spam_report:
            return spam_report.report
        return 0