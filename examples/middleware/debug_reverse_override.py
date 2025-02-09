class DebugReverseOverrideMiddleware:
    """
    Middleware to override reverse() for `post_detail` in DEBUG mode.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        from django.urls import reverse as django_reverse

        def custom_reverse(name, *args, **kwargs):
            if name == "post_detail":
                return "#"
            return django_reverse(name, *args, **kwargs)

        # Monkey-patch the reverse function
        import django.urls
        django.urls.reverse = custom_reverse

        response = self.get_response(request)
        return response
