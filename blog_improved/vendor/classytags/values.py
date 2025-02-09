from datetime import datetime
from django.utils.dateparse import parse_datetime

class DateTimeValue:
    errors = {
        'invalid': "Invalid datetime value: %(value)s",
    }
    value_on_error = None

    def __init__(self, var):
        self.var = var
        try:
            self.literal = self.var.literal
        except AttributeError:
            self.literal = self.var.token

    def resolve(self, context):
        resolved = self.var.resolve(context)
        return self.clean(resolved)

    def clean(self, value):
        if isinstance(value, datetime):
            return value  # Already a datetime object
        
        if isinstance(value, str):
            parsed = parse_datetime(value)
            if parsed is not None:
                return parsed
            
        return self.error(value, 'invalid')

    def error(self, value, category):
        data = self.get_extra_error_data()
        data['value'] = repr(value)
        message = self.errors.get(category, "") % data
        
        if settings.DEBUG:
            raise template.TemplateSyntaxError(message)
        else:
            # warnings.warn(message, template.TemplateSyntaxError)
            return self.value_on_error

    def get_extra_error_data(self):
        return {}

