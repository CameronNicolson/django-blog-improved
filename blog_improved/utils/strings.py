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
            if type(item) is str:
                kwargs[key] = split_string(item)
        return func(*args, **kwargs)
    return wrapper

