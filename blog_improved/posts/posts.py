from abc import abstractmethod
from blog_improved.query_request.query import FilterQueryRequest, QueryRequest

class PostList(list):
    def __init__(self, post_list=None, category=None, date_generated=None, publish_status=None, fetch_command=None, max_num_posts=None):
        super().__init__(post_list)
        self._category = category
        self._date_generated = date_generated
        self._max_num_posts = max_num_posts
        self._publish_status = publish_status
        self._fetch_command = fetch_command

    def fetch_posts(self):
        self._fetch_command.retrieve()

class IgnoreCase:
    def __init__(self, ignore_value):
        self.ignore_value = ignore_value


class PostListBuilder:
    @abstractmethod
    def categories(self, category_list):
        pass

    @abstractmethod
    def max_num_posts(self, n):
        pass
    
    @abstractmethod
    def publish(self, status):
        pass

    @abstractmethod
    def ignored(self, ignore_case_list):
        pass

class PostListQueryRequest(PostListBuilder):

    def __init__(self):
        self._categories = list()
        self._ignored_cases = tuple()
        self._max_size = 40
    
    @property
    def categories(self):
        return self._categories

    def set_max_size(self, number):
        if not isinstance(number, (int, float)):
            raise TypeError(self.__class__.__name__ + " takes a standard number type.")
        self._max_size = int(number)
        return self

    def set_categories(self, categories):
        if not isinstance(categories, list):
            raise TypeError("PostListQuerySet setting categories requires a list")
        # wildcard check
        if "all" in categories or "*" in categories:
            self._categories = None
        else:
            self._categories = categories
        return self
    
    @property
    def ignored_cases(self):
        return self._ignored_cases

    def set_ignored_cases(self, ignored_cases):
        if not isinstance(ignored_cases, tuple):
            raise TypeError("PostListQuerySet setting ignored cases requires a tuple")
        self._ignored_cases = ignored_cases
        return self

    def build(self):
        request = QueryRequest("blog_improved", "Post", [])
        if self._categories:
            request = FilterQueryRequest(queryset_request=request, 
                                        lookup_field="category__name", 
                                        lookup_value=self.categories,
                                        inner_join=["category"])
        for case in self._ignored_cases:
            lp_field, lp_type, lp_value = case
            request = FilterQueryRequest(queryset_request=request,
                                            negate=True, 
                                            lookup_field=lp_field, 
                                            lookup_value=lp_value, 
                                            lookup_type=lp_type)
        post_list = request.make_request()
        return PostList(post_list=post_list, fetch_command=request)
