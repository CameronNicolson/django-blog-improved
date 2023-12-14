from django import forms
from taggit.models import Tag
from .models import Comment, Post, Callback

from crispy_forms_gds.helper import FormHelper
from crispy_forms_gds.layout import Accordion, AccordionSection, Button, HTML, Layout, Field, Fieldset, Size, Submit
from crispy_forms_gds.choices import Choice
from phonenumber_field import formfields
from django.core.exceptions import ValidationError
from itertools import chain
from django.core.validators import integer_validator


class FilterForm(forms.Form):

    category = forms.MultipleChoiceField(
        choices=(),
        widget=forms.CheckboxSelectMultiple,
        label="Filter by topic",
        help_text="Select all boxes that interest you.",
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super(FilterForm, self).__init__(*args, **kwargs)
        category_initial = self.initial.get("category", None)
        self.add_category_field()
        self.helper = FormHelper()
        if category_initial: 
            filter_summary = f"{len(category_initial)} selected"
        else: 
            filter_summary = ""
        self.helper.layout = Layout(
                Accordion(
                    AccordionSection("Topic", "category", summary=f"{filter_summary}"),
                ),
                Submit("submit", "Apply filter", css_class="govuk-button--secondary"),
        )

    def add_category_field(self):
        post_queryset = Post.objects.all().values("category",)
        tags_qs = Tag.objects.filter(id__in=post_queryset).order_by("name")
        tags = [(tag.id, tag.name,) for tag in tags_qs]
        # featured tags - they appear top of the list
        topic_choices=(*tags,)
        self.fields["category"].choices = topic_choices 
        # custom error msg
        self.fields["category"].error_messages = {"required": "Selecting at least one option is required"}

    def clean_category(self):
        cleaned_data = super().clean()
        category_list = cleaned_data["category"]
        for cat in category_list:
            integer_validator(cat)
        return category_list
    
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("name", "email", "body")


class CallbackForm(forms.Form):
    title = "How can I reach you?"
    receipt_name = forms.CharField(
        label="Name",
        widget=forms.TextInput(),
        error_messages={
            "required": "Cannot leave name blank, enter a name."
        }
    )
    telephone_number = formfields.PhoneNumberField(
        label="Telephone",
        help_text="Landline or mobile.",
        widget=forms.TextInput(),
        error_messages={
            "required": "Cannot leave number blank, enter a number."
        }
    )

    note = forms.CharField(
        label="Reason for call",
        help_text="Enter up to 500 characters.",
        widget=forms.Textarea(),
        error_messages={
            "required": "Cannot leave note blank. a reason for your call."
        }
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                Field.text("receipt_name"),
                Field.text("telephone_number"),
                Field.text("note"),
            ),
            HTML("<div class='govuk-hint''>By pressing \"Submit\" "
                 "you agree for <name-of-site> to hold your details "
                 "for a period of time</div>"),
            Button("submit", "Submit"),
        )

    def clean_telephone_number(self):
        telephone = self.cleaned_data["telephone_number"]
        if Callback.objects.filter(telephone_number=telephone).exists():
            self.add_error(field=None, error=ValidationError("We have already received your details. You are prevented from submitting again", code="offense",))
        return telephone


    def save(self):
        data = self.cleaned_data
        callback = Callback(
            receipt_name=data['receipt_name'],
            telephone_number=data['telephone_number'],
            note=data['note'])
        callback.save()
