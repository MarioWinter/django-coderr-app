from rest_framework.pagination import PageNumberPagination

class OffersSetPagination(PageNumberPagination):
    """
    Pagination class for offers with a fixed page size.
    """
    page_size = 6
    page_size_query_param = 'page_size'
    max_page_size = 6