from django.core.paginator import Paginator, Page


def paginate_list(object_list: list, page_number: int = 1, per_page: int = 50) -> Page:
    paginator = Paginator(object_list, per_page)
    return paginator.get_page(page_number)
