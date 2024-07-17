from django.urls import path
from .views import ContactView, SpamView, SearchContactByNamePhone

urlpatterns = [
    path('contacts', ContactView.as_view(), name='add_list_contacts'),
    path('report/spam', SpamView.as_view(), name='report_spam'),
    path('contact/search', SearchContactByNamePhone.as_view(), name='search_contact_by_name_phone')
]