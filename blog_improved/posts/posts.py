from itertools import chain
from abc import ABC, abstractmethod
from enum import Enum
from django.utils import timezone
from django.db.models import F, Window, When, Case, Value, IntegerField
from django.db.models.functions import RowNumber
from blog_improved.query_request.query import FilterQueryRequest, LimitQueryRequest, QueryRequest, QueryRequestSelectValues
from blog_improved.query_request import AnnotateQueryRequest, SortQueryRequest

class PostList(list):
    
    class Field(Enum):
        PK = 0
        TITLE = 1
        HEADLINE = 2
        AUTHOR = 3
        PUBLISHED_ON = 4
        CONTENT = 5
        CATEGORY = 6
        IS_FEATURED = 7
        SLUG = 8
        FIELD_COUNT = 9

    class PriorityOrder:
        FEATURE = 0
        PROMOTED = 1
        NORMAL = 2

    def __init__(self, post_list=None, date_generated=None, publish_status=None, fetch_posts=None, fetch_categories=None, priority_order=None):
        if post_list:
            super().__init__(post_list)
        else:
            super().__init__()

        self._categories = None
        self._date_generated = date_generated
        self._publish_status = publish_status
        self._fetch_posts = fetch_posts
        self._fetch_categories = fetch_categories
        self._priority_ordering = priority_order or [(v[0], PostList.PriorityOrder.NORMAL,) for v in self]

    def categories(self):
        self._categories = self._fetch_categories.retrieve()
        return self._categories

    def fetch_posts(self):
        self.__init__(
                self._fetch_posts.retrieve()
        )
        return self

    def get_priority_order(self):
        return self._priority_ordering

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
        self._post_fields = ("pk", "title", "headline", "author__username", "published_on", "content", "category__name", "is_featured", "slug", "priority",)
    
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
        if not self._num_featured:
            self._num_featured = 1

        self._num_featured = 1
        return self

    def number_of_featured(self, number):
        if not isinstance(number, (int, float)):
            raise TypeError(self.__class__.__name__ + " takes a standard number type.")
        if number <= 0:
            if self._num_featured:
                self._num_featured = 1
            else:
                self._num_featured = 0
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

    def combine_featured_and_latest(self, featured, latest_posts, max_size):
        # Create a set for tracking seen items to avoid duplicates
        seen = set()

        # Start with the featured items
        result = []
        for item in featured:
            post_ident = item[0] 
            if post_ident not in seen:
                result.append(item)
                seen.add(post_ident)
                # Stop if we've reached the max size
                if len(result) == max_size:
                    return result

        # Add remaining items from the latest_posts, avoiding duplicates
        for item in latest_posts:
            post_ident = item[0]
            if post_ident not in seen:
                result.append(item)
                seen.add(post_ident)
                # Stop if we've reached the max size
            if len(result) == max_size:
                return result

        # Return the combined list (guaranteed to be within max_size)
        return result

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

        request = QueryRequestSelectValues(queryset_request=request, fields=self._post_fields)

        request = SortQueryRequest(queryset_request=request, sort_by=["priority", "-published_on"], priority=19)
        nib = Value(PostList.PriorityOrder.NORMAL, output_field=IntegerField())
        request = AnnotateQueryRequest(queryset_request=request, name="priority", calculation=nib, priority=18)


        if self._max_size:
            request = LimitQueryRequest(queryset_request=request, offset=0, max_limit=self._max_size)
 
        featured_request = None
        if self._featured:
            request.make_request()
            featured_request = QueryRequest("blog_improved", "Post", request.get_methods(), return_type="values_list")
            featured_request.add_selected_fields(request.get_selected_fields())
            find_priority = Case(When(is_featured=True, then=Value(0)), output_field=IntegerField())
            featured_request = FilterQueryRequest(queryset_request=featured_request, 
                                        lookup_field="is_featured", 
                                        lookup_value=True)
            featured_request = LimitQueryRequest(queryset_request=featured_request, offset=0, max_limit=self._num_featured) 
            featured_request = AnnotateQueryRequest(queryset_request=featured_request, name="priority", calculation=find_priority, priority=18)

    
        request.make_request()
        post_list = None
        if not featured_request:
            post_list = request.evaluate()
        else:
            featured_request.make_request()
            featured_posts = list(featured_request.evaluate())
            latest_posts = list(request.evaluate())
            post_list = self.combine_featured_and_latest(featured_posts, 
                                        latest_posts,
                                        self._max_size)
 
       # Initialize the new tuples
        new_data = []
        priority_order = []
        # Process each tuple
        last_field = PostList.Field.FIELD_COUNT.value - 1 
        priority_pos = last_field + 1
        for item in post_list:
            new_tuple = item[:priority_pos] + item[priority_pos + 1:]
            priority_order.append((item[0], item[priority_pos],))
            new_data.append(new_tuple)
        return PostList(post_list=new_data, date_generated=timezone.now(), fetch_posts=request, fetch_categories=None, priority_order=priority_order)
