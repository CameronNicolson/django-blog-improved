from django import forms

from .models import Comment, Callback

from crispy_forms_gds.helper import FormHelper
from crispy_forms_gds.layout import Submit
from crispy_forms_gds.layout import Button, HTML, Layout, Field, Fieldset
from phonenumber_field import formfields
from django.core.exceptions import ValidationError


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