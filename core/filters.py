import django_filters
from .models import Item
# from django_filters import CharFilter


class ItemFilter(django_filters.FilterSet):
    class Meta:
        model = Item
        fields = ['name', 'category']
