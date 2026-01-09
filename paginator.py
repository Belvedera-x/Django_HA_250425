from rest_framework.pagination import CursorPagination

class MyCursorPaginator(CursorPagination):
    ordering = 'id'
    page_size = 6

    def get_queryset(self, view):
        return view.get_queryset()