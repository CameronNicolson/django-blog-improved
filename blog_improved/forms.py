from django import forms
from taggit.models import Tag
from .models import Comment, Post, Callback

from crispy_forms_gds.helper import FormHelper
from crispy_forms_gds.layout import Button, HTML, Layout, Field, Fieldset, Submit
from phonenumber_field import formfields
from django.core.exceptions import ValidationError
from itertools import chain

class FilterForm(forms.Form):

    def __init__(self, category=True, *args, **kwargs):
        super(FilterForm, self).__init__(*args, **kwargs)
        self.category = category
        if self.category:
            self.add_category_field()

        self.helper = FormHelper()
        self.helper.layout = Layout("category", 
                                    Submit("submit", "Apply filter", css_class="govuk-button--secondary"),)

    def add_category_field(self):
        post_queryset = Post.objects.all().values("category",)
        tags_qs = Tag.objects.filter(id__in=post_queryset).order_by("name")
        tags = [(tag.id, tag.name,) for tag in tags_qs]
        # featured tags - they appear top of the list
        featured_tags = [("99999", "All Topics",)]
        self.fields["category"] = forms.ChoiceField(
        choices=((*featured_tags, *tags)),
            label="category",
        ) 

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
