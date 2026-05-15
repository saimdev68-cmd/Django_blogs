
class OrderMixin:
    def filter(self,queryset):
        order = self.request.GET.get("order")
        if order == 'new':
            queryset = queryset.order_by("-published_at")
        else:
            queryset = queryset.order_by("published_at")
        return queryset