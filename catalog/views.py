from django.contrib.postgres.search import TrigramSimilarity
from rest_framework import generics
from unicodedata import category

from .models import Product, Category
from .serializers import ProductSerializer, CategorySerializer
from django.db.models import Q


class ProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer
    def get_queryset(self):
        qs = (
            Product.objects
            .filter(is_active=True)
            .select_related('category')
            .prefetch_related('variants', "images")
        )
        '''
        category_slug = self.request.query_params.get('category')
        q = self.request.query_params.get('q')
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')

        if category_slug:
            qs = qs.filter(category__slug = category_slug)

        if q:
            qs = qs.filter(
                Q(title__icontains=q) |
                Q(description__icontains=q) |
                Q(variants__sku__icontains=q) |
                Q(variants__attributes_text__icontains=q)
            ).distinct()

        if min_price:
            qs = qs.filter(variants__price_amount__gte=min_price).distinct()

        if max_price:
            qs = qs.filter(variants__price_amount__lte=max_price).distinct()

        return qs
        '''

        q = self.request.query_params.get('q')
        if not q:
            return qs.distinct()

        #1) Normal qidiruv (meaningful)
        normal = qs.filter(
            Q(title__icontains=q) |
            Q(description__icontains=q) |
            Q(variants__sku__icontains=q) |
            Q(variants__attributes_text__icontains=q)
        ).distinct()

        if normal.exists():
            return normal

        #2) Trigram fallback (typo tolerant)
        trigram = (
            qs.annotate(
                sim = (
                    TrigramSimilarity("title", q)+
                    TrigramSimilarity("variants__sku", q)+
                    TrigramSimilarity("variants__attributes_text", q)
                )
            )
            .filter(sim__gt=0.2)
            .order_by('-sim')
            .distinct()
        )

        return trigram


class ProductDetailView(generics.RetrieveAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        return (
            Product.objects
            .filter(is_active=True)
            .select_related('category')
            .prefetch_related('variants')
        )


class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

