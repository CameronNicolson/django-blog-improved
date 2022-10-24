import re
from django.shortcuts import render
from blog.forms import CallbackForm
from blog.models import Callback
from django.core.exceptions import NON_FIELD_ERRORS
from django.views.generic import FormView, TemplateView
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse
from utils.prettify_url import *

def about(request):
    return render(request, "pages/about.html")

def service(request):
    return render(request, "pages/services.html")

def cv(request):
    return render(request, "pages/cv.html")

def license(request):
    return render(request, 'pages/license.html')

def contact(request):
    return render(request, "pages/contact.html")

def projects(request):
    return render(request, "pages/projects.html")


class BasicForm(SuccessMessageMixin, FormView):
    template_name = "pages/form-page.html"
    success_url = "success"
    
    def get_success_message(self, cleaned_data):
        messages.add_message(self.request, messages.SUCCESS, 'Form complete', extra_tags="transaction_status")
        for field_name, field in cleaned_data.items():
            msg = "{0}: {1}".format(field_name, field)
            messages.add_message(self.request, messages.SUCCESS, msg)

    def get_form_class(self):
        test = self.request.resolver_match.url_name
        enabled_forms = {"call-request": CallbackForm}
        return enabled_forms[test]
    
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        try: 
            form_title = self.get_form().title
        except AttributeError:
            form_title = prettify_url(self.request.resolver_match.view_name)
        context["title"] = form_title
        return context

class CallRequestForm(BasicForm):
    reference_messages = [
        "Your name: %(receipt_name)s",
        "Your number: %(telephone_number)s",
    ]

    additiona_action_messages = [
        "The system has now notified me of your request. You can expect a response soon.",
        "Generally, if you have not heard back within a week, then I have probably dismissed your request.",
    ]

    def get_success_message(self, cleaned_data):
        messages.add_message(self.request, messages.SUCCESS, 'Contact sent', extra_tags="transaction_status")
        self.reference_messages[0] = self.reference_messages[0] % dict(receipt_name=cleaned_data["receipt_name"])
        self.reference_messages[1] = self.reference_messages[1] % dict(telephone_number=cleaned_data["telephone_number"])
        for msg in self.reference_messages:
            messages.add_message(self.request, messages.SUCCESS, msg, extra_tags="reference")

        for msg in self.additiona_action_messages:
            messages.add_message(self.request, messages.SUCCESS, msg, extra_tags="additional_action")

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context["crumbs"] = [
            ("Home", reverse("home"),),
            ("Contact", reverse("contact"),),
            (context["title"], None,),
        ]
        return context


class SuccessFormCreation(TemplateView):
    template_name = "confirmation.html"