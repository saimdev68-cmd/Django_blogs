from .models import Article , Comment
from .mixins import OrderMixin 
from .forms import CommentForm
from django.views import generic , View
from django.shortcuts import  redirect , get_object_or_404
from django.urls import  reverse
from django.db.models import Q , Count , Prefetch
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator

# Create your views here.

class HomeView(generic.TemplateView):
    template_name = "index.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        base_qs = Article.objects.filter(is_published=True).select_related("category")
        context["is_top"] = base_qs.filter(is_top=True)[:4]
        context["is_trending"] = base_qs.filter(is_trending=True,is_top=False)[:3]
        context["latest"] = base_qs.filter(is_top=False,is_trending=False)[:7]
        return context
    
class CategoryArticleView(OrderMixin,generic.ListView):
    template_name = "category_article.html"
    context_object_name = "articles"
    paginate_by = 10

    def get_queryset(self):
        queryset = Article.objects.filter(is_published=True,category__slug=self.kwargs["slug"]).select_related("category")
        return self.filter(queryset)

class OtherArticleView(OrderMixin,generic.ListView):
    template_name = "category_article.html"
    context_object_name = "articles"
    paginate_by = 10

    def get_queryset(self):
        queryset = Article.objects.filter(category__isnull=True,is_published=True)
        return self.filter(queryset)
    
class SearchArticleView(generic.ListView):
    template_name = "category_article.html"
    context_object_name = "articles"
    paginate_by = 10

    def get_queryset(self):
        queryset = Article.objects.filter(is_published=True)
        q = self.request.GET.get("q")
        if q:
            queryset = queryset.filter(
                Q(title__icontains=q) |
                Q(category__name__icontains=q)
            )
        return queryset
    
class ArticleDetailView(generic.DetailView):
    template_name = "article_detail.html"
    context_object_name = "article"
    model = Article

    def get_queryset(self):
        return ( Article.objects.filter(is_published=True).
            select_related("category").
            prefetch_related("paragraph","likes").
            annotate(total_comments=Count("comments",distinct=True),total_likes=Count("likes",distinct=True))
        )
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        comment_list = ( Comment.objects.filter(article=self.object)
        .select_related("profile","profile__user")
        )
        pagintor = Paginator(comment_list,5)
        page_number = self.request.GET.get("page")
        comments = pagintor.get_page(page_number)
        context["comments"] = comments
        context["form"] = CommentForm()
        context["total_comments"] = self.object.total_comments
        context["total_likes"] = self.object.total_likes
        return context
    
    def post(self,request,*args, **kwargs):

        if not request.user.is_authenticated:
            return redirect ("login")
        self.object = self.get_object()
        if Comment.objects.filter(profile=request.user.profile,article=self.object).exists():
            return redirect ("article:detail",pk=self.object.pk)
        
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.profile = request.user.profile
            comment.article = self.object
            comment.save()
            return redirect ("article:detail",pk=self.object.pk)
        context = self.get_context_data()
        context["form"] = form
        return self.render_to_response(context)
    
class CommentUpdateView(LoginRequiredMixin,generic.UpdateView):
    template_name = "comment_update.html"
    model = Comment
    form_class = CommentForm

    def get_queryset(self):
        return Comment.objects.filter(profile=self.request.user.profile)
    
    def get_success_url(self):
        return reverse("article:detail",kwargs={"pk":self.object.article.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["article"] = self.object.article
        return context
    
class CommentDeleteView(LoginRequiredMixin,generic.DeleteView):
    model = Comment
    
    def get_queryset(self):
        return Comment.objects.filter(profile=self.request.user.profile)

    def get_success_url(self):
        return reverse("article:detail",kwargs={"pk":self.object.article.pk})
    
class LikeView(LoginRequiredMixin, View):
    def post(self, request, pk):
        article = get_object_or_404(Article, pk=pk)
        profile = request.user.profile
        if article.likes.filter(id=profile.id).exists():
            article.likes.remove(profile)
        else:
            article.likes.add(profile)
        return redirect("article:detail", pk=article.pk)

class BookmarkView(LoginRequiredMixin,View):
    def post(self,request,pk):
        article = get_object_or_404(Article,pk=pk)
        profile = request.user.profile
        if article.bookmark.filter(id=profile.id).exists():
            article.bookmark.remove(profile)
        else:
            article.bookmark.add(profile)
        return redirect ("article:detail",pk=article.pk)
    
class BookmarkListView(LoginRequiredMixin,OrderMixin,generic.ListView):
    template_name = "category_article.html"
    context_object_name = "articles"
    paginate_by = 10

    def get_queryset(self):
        queryset = Article.objects.filter(bookmark=self.request.user.profile)
        return self.filter(queryset)
