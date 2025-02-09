from classytags.values import StringValue, ListValue
from classytags.utils import TemplateConstant
from classytags.arguments import MultiKeywordArgument

class CommaSeperatableMultiKeywordArgument(MultiKeywordArgument):
    def __init__(self, name, default=None, required=True, resolve=True,
                 defaultkey=None, splitter="=", delimiter=",", commakwargs=None):
        super().__init__(name, default, required, resolve, defaultkey, splitter)
        if not isinstance(delimiter, str):
            raise ValueError("Delimiter must be a character.")
        self.delimiter = delimiter
        self.commakwargs = commakwargs or []

    def parse_token(self, parser, token):
         # Call the parent method to get the token parsed as usual
        options = super().parse_token(parser, token)
        key, value = options

        # Check if the key is in the list that requires comma-splitting
        if key in self.commakwargs:
            if isinstance(value, StringValue):
                # Split the resolved value and handle the empty case
                resolved_value = value.resolve(None)
                if resolved_value:  # Only proceed if resolved_value is not empty or None
                    list_values = [TemplateConstant(item) for item in resolved_value.split(self.delimiter)]
                    # Initialize the ListValue with the first item, if any
                    template_list = ListValue(list_values[0]) if list_values else ListValue()
                    # Append remaining values, if any
                    template_list.extend(list_values[1:])
                    # Update options with the new ListValue
                    options = (key, template_list)
        return options
