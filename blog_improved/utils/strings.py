from functools import wraps

def split_string(input_string, delimiter=','):
    """
    Splits a string into a list of strings based on the specified delimiter, 
    trimming whitespace from each element.
    
    Args:
    input_string (str): The string to split.
    delimiter (str, optional): The delimiter to use for splitting the string. Defaults to ','.
    
    Returns:
    list: A list of trimmed strings.
    """
    try:
        input_string = str(input_string)
    except ValueError:
        return None
    return [element.strip() for element in input_string.split(delimiter) if element.strip()]

def convert_str_kwargs_to_list(func):
    """
    Decorator that converts string keyword arguments into lists of strings.

    This decorator is used to automatically convert any string keyword arguments
    passed to the decorated function into lists of strings, based on a specified
    delimiter. The conversion is performed using the `split_string` function.

    Args:
        func (callable): The function to be decorated.

    Returns:
        callable: The wrapped function with converted keyword arguments.

    The `split_string` function used for conversion splits the string by commas (',')
    and trims any whitespace around the resulting elements. Empty strings are removed
    from the resulting list.

    Example:
        @convert_str_kwargs_to_list
        def my_function(**kwargs):
            return kwargs

        result = my_function(arg1="apple,banana,cherry", arg2="foo, bar , baz", arg3=42)
        # result:
        # {
        #     'arg1': ['apple', 'banana', 'cherry'],
        #     'arg2': ['foo', 'bar', 'baz'],
        #     'arg3': 42
        # }

    Usage Notes:
        - Only string keyword arguments are converted. Non-string arguments remain unchanged.
        - The conversion uses the default comma delimiter and is case-sensitive by default.

    """
    def wrapper(*args, **kwargs):
        for key, item in kwargs.items():
            if isinstance(item, str):
                kwargs[key] = split_string(item)
        return func(*args, **kwargs)
    return wrapper


class StringAppender(str):
    def __init__(self, value=None):
        self._value = value

    def __add__(self, other):
        other = " " + other
        return StringAppender(super().__add__(other))

    def __iadd__(self, other):
        return self + other
   #     if self._value:
    #        other = f"{self._value} {other}" 
     #   else:
      #      self._value = other
       # return self + 

    def get_value(self):
        return self._value

    def get_value_list(self):
        return self._value.split(" ")

def to_string_appender(func):
#    """Decorator that ensures the returned value from func is a StringAppender."""
    def wrapper(value):
        if not isinstance(value, str):
            value = str(value)
        value = StringAppender(value)
        return func(value)
    return wrapper

def strip_whitespace(func_or_value):
    # If the input is callable, treat it as a decorator
    if callable(func_or_value):
        @wraps(func_or_value)
        def wrapper(value):
            if not isinstance(value, str):
                value = str(value)
            value = value.strip()
            return func_or_value(value)
        return wrapper
    # Otherwise, treat it as a normal function
    else:
        if not isinstance(func_or_value, str):
            func_or_value = str(func_or_value)
        return func_or_value.strip()

def normalise_extra_whitespace(func):
    def wrapper(value):
        parts = value.split()
        normalised = " ".join(parts)
        return func(normalised)
    return wrapper

def validate_regex(pattern):
    from re import match
    def decorator(func):
        def wrapper(value):
            if not match(pattern, value):
                raise ValueError(f"Value '{value}' does not match pattern {pattern}")
            return func(value)
        return wrapper
    return decorator
