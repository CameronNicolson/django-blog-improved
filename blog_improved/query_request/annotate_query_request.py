from django.db.models import (Window, ExpressionWrapper, F, 
                              Value, Case, When, Func
)
from blog_improved.query_request.query import QueryRequestDecorator 

class AnnotateQueryRequest(QueryRequestDecorator):
    def __init__(self, queryset_request=None, name=None, calculation=None, priority=10):
        """
        Initialize the AnnotateQueryRequest class.

        :param queryset_request: The QueryRequest object to decorate.
        :param name: The name of the annotation field.
        :param calculation The object used for calculation (e.g., a Case, Func, or F instance).
        :param priority: Priority for applying this annotation in the request pipeline.
        """
        super().__init__(queryset_request=queryset_request)

        if not name or calculation is None:
            raise ValueError("You must provide 'name' and 'calculation_object'.")

        # Validate the calculation's type
        valid_types = (Case, Func, F, Value, Window, ExpressionWrapper)
        if not isinstance(calculation, valid_types):
            raise TypeError(f"calculation must be one of {valid_types}, got {type(calculation_object)}")

        # Store the annotation details
        self._annotation = {
            name: calculation
        }
        self._priority = priority

    def make_request(self):
        """
        Apply the annotation to the QuerySet.
        """
        annotation_method = ("annotate", (), self._annotation, self._priority)
        self.get_request().get_methods().append(annotation_method)

        return self._queryset_request.make_request()
