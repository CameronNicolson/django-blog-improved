from django import template
from django.db.models.query import QuerySet
from django.utils import timezone
from blog_improved.models import Post
from blog_improved.utils.strings import convert_str_kwargs_to_list

register = template.Library()

class BlogPostList:
    def __init__(self, num_of_posts, date_generated, categories, status_codes):
        self._num_of_posts = num_of_posts
        self._date_generated = date_generated 
        self._categories = categories 
        self._status_coes = status_codes

class QueryCommand:
    def __init__(self, initial_queryset=None, *args, **kwargs):
        self._initial_queryset = initial_queryset
        self._args = args
        self._kwargs = kwargs
    
    def _filter_or_exclude(self, negate=False, queryset=None, **lookups) -> QuerySet:
        if queryset == None:
            raise AssertionError("Parameter queryset was not provided")
        if negate:
            return queryset.exclude(**lookups)
        return queryset.filter(**lookups)

    def _sort(self, queryset=None, field_name=None, order=None) -> QuerySet:
        if order == "desc":
            field_name = ("-" + field for field in field_name)
        return queryset.order_by(*field_name)

    def execute(self) -> QuerySet:
        # Get all returns a new queryset that includes all records from the database table corresponding to the model
        return self._initial_queryset.values(*self._args)

class CategoryFilter(QueryCommand):
    def __init__(self, command=None, category_names=None, category_db_fieldname="category", *args, **kwargs):
        super().__init__(command._initial_queryset, command._args, command._kwargs)
        self._command = command
        self._category_names = category_names
        self._category_db_fieldname = category_db_fieldname

    def execute(self):
        queryset = self._command.execute()
        lookups = {f"{self._category_db_fieldname}__name__in": self._category_names}
        result = self._filter_or_exclude(negate=False, queryset=queryset, **lookups)
        return result

class OrderByFieldName(QueryCommand):
    def __init__(self, command=None, field_name=None, order=None, *args, **kwargs):
        super().__init__(command._initial_queryset, command._args, command._kwargs)
        self._command = command
        if(order not in ["asc", "desc"]):
            raise ValueError("Order must be 'asc' or 'desc'")
        self._field_name = field_name
        self._order = order
     
    def execute(self):
        queryset = self._command.execute()
        hi = self._sort(queryset, self._field_name, self._order)
        print(hi.query)
        return hi


class QueryList:
    def __init__(self, command_list=None):
        self._command_list = command_list or list()

    def register_query(self, cmd):
        self._command_list.append(cmd)

    def fetch_posts(self):
        for cmd in self._command_list:
            cmd.execute()

class TimeOfDayFilter(QueryCommand): 
    def __init__(self, command=None, current_time=None, time_divisions=None, *args, **kwargs):
        super().__init__(command._initial_queryset, command._args, command._kwargs)
        self._command = command
        self._current_time = current_time or timezone.now()
        self._time_divisions = time_divisions or [0, 12, 17, 21,]
 
    def matches_time_of_day(self, first_time, second_time):
        a = time_of_day(first_time)
        b = time_of_day(second_time)
        return a == b

    def next_greater_time(self, hour): 
        # Iterate through the sorted list to find the next greater element
        for num in self._time_divisions:
            if num > hour:
                return num
        return None  # Return None if no greater element is found

    def time_of_day(self, hours: int, afternoon=12, evening=19, night=21):
        morning, afternoon, evening, night = self._time_divisions
        if morning <= hours < afternoon:
            return morning
        elif afternoon <= hours < evening:
            return afternoon
        elif evening <= hours < night:
            return evening
        elif night <= hours < 24:
            return night
        else:
            return ValueError("The paramters are not in the 24-hour format range")


    def execute(self):
        queryset = self._command.execute()
        print("timedate hour")
        print(timezone.now().hour)
        start_time = self.time_of_day(self._current_time.hour)
        end_time = self.next_greater_time(start_time) 
        print(start_time)
        hi = queryset.filter(published_on__hour__gte=start_time, 
                             published_on__hour__lt=end_time)
        print("this is time_of_day filter")
        print(hi)
        print(hi.query)
        return hi

blog_common_commands = {
        "time_of_day": TimeOfDayFilter
}

def custom_filters(filter_names, func, command_list=blog_common_commands):
    if isinstance(filter_names, str):
        filter_names = [filter_names]
    cmd = None
    try:
        for name in filter_names:
            cmd = command_list[name](command=func)
    except KeyError:
        raise AssertionError("Custom filter {name} was not found")
    # filter_names was empty, run func anyways
    if cmd == None:
        return func
    return cmd

@convert_str_kwargs_to_list
def bloglist(*args, **kwargs):
    print(kwargs)
    queryset = QuerySet(model=Post, query=Post.public.get_queryset().query) 
    print("what is it")
    print(queryset)
    query_list = QueryList({
        custom_filters(["time_of_day"],
            OrderByFieldName( 
                command=CategoryFilter(command=QueryCommand(queryset, *("title", "headline", "published_on",)), category_names=kwargs["category"]),
                field_name=["published_on", "is_featured"],
                order="desc",
            )
        )
    })
    return query_list.fetch_posts()   

