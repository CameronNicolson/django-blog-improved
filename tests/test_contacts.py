from django.test import TestCase
from django.contrib.sites.models import Site
from blog_improved.models import Contact, EmailAddress, SiteSettings

class TestContacts(TestCase):
    def setUp(self):
        site = Site.objects.first()
        site.name = "news.local"
        site.save()
        self.website = site

    def test_create_contact_with_email(self):
        
        # Create an email address associated with the contact
        email = EmailAddress.objects.create(email_address="john@example.com")

        # Create a new contact
        contact = Contact.objects.create(content_object=email, name="John Doe", notes="Test notes", site=self.website)
        
        # Retrieve the contact from the database
        saved_contact = Contact.objects.get(name="John Doe")

        # Check if the contact and email address were saved correctly
        self.assertEqual(saved_contact.name, "John Doe")
        self.assertEqual(saved_contact.notes, "Test notes")
        self.assertEqual(saved_contact.site.name, "news.local")
        
        # Check if the email address is associated with the contact
        #related_email = saved_contact.contact.first()
        related_email = email.contact.first()
        # Check if the email address is associated with the contact
        self.assertEqual(related_email.name, "John Doe")


    def test_site_settings_can_use_contact_with_email(self):
        email = EmailAddress.objects.create(email_address="django@djangogirls.org")

        # Create a new contact
        contact = Contact.objects.create(content_object=email, name="djangogirls", notes="Speak to Sam for login info", site=self.website)
        saved_contact = Contact.objects.get(name="djangogirls")
         
        site_settings = SiteSettings.objects.create(site=self.website, default_contacts=saved_contact)
        saved_settings = SiteSettings.objects.get(site=self.website)

        self.assertEqual(saved_contact.name, "djangogirls")
        self.assertEqual(saved_contact.site.name, "news.local")

        self.assertEqual(saved_settings.default_contacts.name, "djangogirls")
        related_email = EmailAddress.objects.get(contact=saved_contact)
        self.assertEqual(related_email.email_address, "django@djangogirls.org")
