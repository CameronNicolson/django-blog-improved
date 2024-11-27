from abc import ABC, abstractmethod
from enum import Enum
from django.utils import timezone
from django.db.models import F, Window, When, Case, Value, IntegerField
from django.db.models.functions import RowNumber
from blog_improved.query_request.query import FilterQueryRequest, LimitQueryRequest, QueryRequest, QueryRequestSelectValues
from blog_improved.query_request import AnnotateQueryRequest, SortQueryRequest

class PostList(list):
    
    class Field(Enum):
        TITLE = 0
        HEADLINE = 1
        AUTHOR = 2 
        PUBLISHED_ON = 3
        CONTENT = 4
        CATEGORY = 5
        IS_FEATURED = 6

    def __init__(self, post_list=None, date_generated=None, publish_status=None, fetch_posts=None, fetch_categories=None):
        if post_list:
            super().__init__(post_list)
        else:
            super().__init__()

        self._categories = None
        self._date_generated = date_generated
        self._publish_status = publish_status
        self._fetch_posts = fetch_posts
        self._fetch_categories = fetch_categories

    def categories(self):
        self._categories = self._fetch_categories.retrieve()
        return self._categories

    def fetch_posts(self):
        self.__init__(
                self._fetch_posts.retrieve()
        )
        return self

class IgnoreCase:
    def __init__(self, ignore_value):
        self.ignore_value = ignore_value


class PostListBuilder(ABC):
    @abstractmethod
    def categories(self, categories):
        pass

    @abstractmethod
    def featured(self, active):
        pass

    def number_of_featured(self, number):
        pass

    @abstractmethod
    def max_size(self, number):
        pass
    
    @abstractmethod
    def ignored(self, ignore_cases):
        pass

    @abstractmethod
    def return_type(self, rtype):
        pass

    @abstractmethod
    def status(self, status):
        pass

class PostListQueryRequest(PostListBuilder):

    def __init__(self):
        self._categories = list()
        self._ignored_cases = tuple()
        self._max_size = None
        self._featured = False
        self._num_featured = None
        self._return_type = "instances"
        self._status = 1
    
    def max_size(self, number):
        if not isinstance(number, (int, float)):
            raise TypeError(self.__class__.__name__ + " takes a standard number type.")
        if number < 0:
            self._max_size = None
        else:
            self._max_size = int(number)
        return self

    def categories(self, categories):
        if not isinstance(categories, list):
            raise TypeError("PostListQuerySet setting categories requires a list")
        # wildcard check
        if "all" in categories or "*" in categories:
            self._categories = None
        else:
            self._categories = categories
        return self
    
    def ignored(self, ignored_cases):
        if not isinstance(ignored_cases, tuple):
            raise TypeError("PostListQuerySet setting ignored cases requires a tuple")
        self._ignored_cases = ignored_cases
        return self

    def featured(self, active):
        self._featured = active
        return self

    def number_of_featured(self, number):
        if not isinstance(number, (int, float)):
            raise TypeError(self.__class__.__name__ + " takes a standard number type.")
        if number <= 0:
            self._num_featured = None
        else:
            self._num_featured = int(number)

        if not self._max_size:
           self._max_size = self._num_featured 
        return self

    def return_type(self, rtype):
        self._return_type = rtype
        return self

    def status(self, status):
        self._status = status
        return self

    def build(self):
        request = QueryRequest("blog_improved", "Post", [])
        if self._return_type:
            request.set_return_type(self._return_type)
        if self._status:
            request = FilterQueryRequest(queryset_request=request,
                               lookup_field="status",
                               lookup_value=self._status)
        if self._categories:
            request = FilterQueryRequest(queryset_request=request, 
                                        lookup_field="category__name", 
                                        lookup_value=self._categories,
                                        inner_join=["category", "author"]                       )
        for case in self._ignored_cases:
            lp_field, lp_type, lp_value = case
            request = FilterQueryRequest(queryset_request=request,
                                            negate=True, 
                                            lookup_field=lp_field, 
                                            lookup_value=lp_value, 
                                            lookup_type=lp_type)
        if self._max_size:
            request = LimitQueryRequest(queryset_request=request, offset=0, max_limit=self._max_size)
        if self._featured:
            if self._num_featured and\
                    self._num_featured < self._max_size:
                find_featured = Case(When(is_featured=True, then=Value(0)), default=Value(1), output_field=IntegerField())
                request = AnnotateQueryRequest(queryset_request=request, name="priority", calculation=find_featured)

                request = SortQueryRequest(queryset_request=request, sort_by=["priority"], priority=19)
            else:
                request = FilterQueryRequest(queryset_request=request, 
                                        lookup_field="is_featured", 
                                        lookup_value=True) 

        request = QueryRequestSelectValues(queryset_request=request, fields=("title", "headline", "author__username", "published_on", "content", "category__name", "is_featured"))
        request.make_request()
        post_list = request.evaluate()
         
        return PostList(post_list=post_list, date_generated=timezone.now(), fetch_posts=request, fetch_categories=None)
