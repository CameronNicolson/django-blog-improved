from django.test import TestCase
from django.db.models.query import QuerySet
from blog_improved.models import Post, Tag
from blog_improved.query_request.query import QueryRequest, LimitQueryRequest, FilterQueryRequest

class TestQueryRequest(TestCase):
    fixtures = ["users", "groups", "tags", "posts", "media"]

    def test_base_queryset_request_get_method(self):
        methods = [("only", tuple(["title", "headline",]), dict(), 1)]
        queryset_req = QueryRequest(app_name="blog_improved", model="Post", methods=methods)
        method_info = queryset_req.get_methods() 
        self.assertIsInstance(method_info, list)
    
    def test_base_queryset_exception_attribute(self):
        with self.assertRaisesRegex(AttributeError, "wrong_method_name is not an attribute of QuerySet."):
            QueryRequest(app_name="blog_improved", model="Post", methods=[("wrong_method_name", None, None, 1)])

    def test_base_queryset_request_make_request(self):
        qs_req = QueryRequest(app_name="blog_improved", model="Post", methods=[("all", None, None, 3),]) 
        qs = qs_req.make_request()
        self.assertIsInstance(qs, QuerySet)

    def test_filter_queryset_request_methods(self):
        base_req = QueryRequest("blog_improved", "Post", [("all",None,None,3,)])
        filter_request = FilterQueryRequest(queryset_request=base_req, lookup_field="author", lookup_value=1)
        query = filter_request.make_request()
        method = base_req.get_methods()[1]
        method_name = method[0]
        method_kwargs = method[2]
        method_kwargs_first_key = next(iter(method_kwargs))
        method_kwargs_first_value = next(iter(method_kwargs.values()))
        self.assertEqual(method_name, "filter")
        self.assertEqual(method_kwargs_first_key, "author__exact")
        self.assertEqual(method_kwargs_first_value, 1)


class TestFilterQueryRequest(TestCase):
    fixtures = ["users", "groups", "tags", "posts", "media"]

    def _contains_not(where_node):
        """
        Recursively check if a WhereNode contains a NOT condition.
    
        :param where_node: Instance of WhereNode.
        :return: Boolean indicating presence of NOT condition.
        """
        if isinstance(where_node, NegatedExpression):
            return True

        for child in where_node.children:
            if isinstance(child, WhereNode):
                if contains_not(child):
                    return True
            elif isinstance(child, NegatedExpression):
                return True
        return False


    def test_negatted_method_exclude(self):
        base_req = QueryRequest("blog_improved", "Post", [("all",None,None,3,)])
        filter_request = FilterQueryRequest(queryset_request=base_req, negate=True, lookup_field="pk", lookup_value=63)
        filter_request = filter_request.make_request()
        method = base_req.get_methods()[1]
        method_name = method[0]
        method_kwargs = method[2]
        method_kwargs_first_key = next(iter(method_kwargs))
        method_kwargs_first_value = next(iter(method_kwargs.values()))
        self.assertEqual(method_name, "exclude")
        self.assertEqual(method_kwargs_first_key, "pk__exact")
        self.assertEqual(method_kwargs_first_value, 63)

    def test_filter_with_field_name(self):
        base_req = QueryRequest("blog_improved", "Post", [("all",None,None,3,)])
        filter_request = FilterQueryRequest(queryset_request=base_req, lookup_field="title", lookup_value="snowstorm")
        actual_result = filter_request.get_field_lookup()
        self.assertEqual(actual_result, {"title__exact": "snowstorm"})

    def test_filter_with_single_transform(self):
        base_req = QueryRequest("blog_improved", "Post", [("all",None,None,3,)])
        filter_request = FilterQueryRequest(queryset_request=base_req, lookup_field="name", lookup_transformers=["reverse"], lookup_value="metafive", lookup_type="icontains")
        actual_result = filter_request.get_field_lookup()
        self.assertEqual(actual_result, {"name__reverse__icontains": "metafive"})


    def test_filter_with_multiple_transformers(self):
        base_req = QueryRequest("blog_improved", "Post", [("all",None,None,3,)])
        filter_request = FilterQueryRequest(queryset_request=base_req, lookup_field="name", lookup_transformers=["lower", "first3chars", "reverse"], lookup_value="him", lookup_type="icontains")
        actual_result = filter_request.get_field_lookup()
        self.assertEqual(actual_result, {"name__lower__first3chars__reverse__icontains": "him"})

    def test_filter_sql_WHERE_not_statement(self):
        base_req = QueryRequest("blog_improved", "Post", [("all",None,None,3,)])
        filter_request = FilterQueryRequest(queryset_request=base_req, lookup_field="status", lookup_value=1, lookup_type="exact", negate=True)
        queryset = filter_request.make_request()
        other_queryset = QuerySet(model=Post).exclude(status=1) 
        self.assertEqual(queryset.query.has_filters(), other_queryset.query.has_filters())

    def test_filter_sql_WHERE_AND_statement(self):
        base_req = QueryRequest("blog_improved", "Post", [("all",None,None,3,)])
        first_filter = FilterQueryRequest(queryset_request=base_req, lookup_field="status", lookup_value=1, lookup_type="exact", negate=False)
        second_filter = FilterQueryRequest(queryset_request=first_filter, lookup_field="category", lookup_value=1, lookup_type="exact", negate=False)
        third_filter = FilterQueryRequest(queryset_request=second_filter, lookup_field="title", lookup_value="django", lookup_type="icontains", negate=True)
        queryset = third_filter.make_request()
        other_queryset = QuerySet(model=Post).exclude(title__icontains="django").filter(category=1).filter(status=1).all()
        self.assertEqual(queryset.query.has_filters(), other_queryset.query.has_filters())

    def test_select_related(self):
        # Check colors category exists
        cat = Tag.objects.get(name="colors")
        self.assertEqual((cat.pk, cat.name, cat.slug,), (11, "colors", "colors" )) 
        base_req = QueryRequest("blog_improved", "Post", [("all",None,None,3,)])
        filter_join = FilterQueryRequest(queryset_request=base_req, lookup_field="category__name", lookup_transformers="", lookup_value="colors", inner_join=["category"], negate=False)
        blog_queryset = filter_join.make_request()
        django_queryset = Post.objects.select_related("category").filter(**{"category__name": "colors"})
        self.assertEqual(str(blog_queryset.query), str(django_queryset.query))

class TestLimitQueryRequest(TestCase):
    fixtures = ["users", "groups", "tags", "posts", "media"]

    def test_limit_single_result(self):
        base_req = QueryRequest("blog_improved", "Post", [("all",None,None,3,)])
        limitreq = LimitQueryRequest(queryset_request=base_req, max_limit=1)
        qs = limitreq.make_request()
        self.assertEqual(qs.count(), 1)

    def test_limit_ten_results(self):
        base_req = QueryRequest("blog_improved", "Post", [("all",None,None,3,)])
        limitreq = LimitQueryRequest(queryset_request=base_req, offset=0, max_limit=10)
        qs = limitreq.make_request()
        self.assertEqual(qs.count(), 10)

    def test_limit_throw_value_error(self):
        base_req = QueryRequest("blog_improved", "Post", [("all",None,None,3,)])
        with self.assertRaisesRegex(ValueError, "Negative integers are not allowed."):
            limitreq = LimitQueryRequest(queryset_request=base_req, max_limit=int(-2))

    def test_limit_throw_type_error(self):
        base_req = QueryRequest("blog_improved", "Post", [("all",None,None,3,)])
        # offset is int and max_limit is str
        with self.assertRaisesRegex(TypeError, "The limit and offset values must be integers."):
            limitreq = LimitQueryRequest(queryset_request=base_req, offset=0, max_limit="440")
        # offset is str and max_limit is int
        with self.assertRaisesRegex(TypeError, "The limit and offset values must be integers."):
            limitreq = LimitQueryRequest(queryset_request=base_req, offset="hello", max_limit=67)
        # both offset and max_limit are strings
        with self.assertRaisesRegex(TypeError, "The limit and offset values must be integers."):
            limitreq = LimitQueryRequest(queryset_request=base_req, offset="2", max_limit="33")

