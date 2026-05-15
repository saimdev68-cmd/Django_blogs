from django.urls import path
from .views import (
    HomeView,
    CategoryArticleView,
    OtherArticleView,
    SearchArticleView,
    ArticleDetailView,
    BookmarkView,
    LikeView,
    CommentUpdateView,
    CommentDeleteView,
    BookmarkListView
)

app_name = "article"

urlpatterns = [
    path("",HomeView.as_view(),name="home"),
    path("search",SearchArticleView.as_view(),name="search"),
    path("<slug:slug>/",CategoryArticleView.as_view(),name="category"),
    path("other/",OtherArticleView.as_view(),name="other"),
    path("article/<int:pk>/",ArticleDetailView.as_view(),name="detail"),
    path("article/comment/<int:pk>/",CommentUpdateView.as_view(),name="comment_update"),
    path("article/comment/<int:pk>/delete/",CommentDeleteView.as_view(),name="comment_delete"),
    path("article/<int:pk>/like/",LikeView.as_view(),name="like"),
    path("article/<int:pk>/bookmark/",BookmarkView.as_view(),name="bookmark"),
    path("article/bookmark/",BookmarkListView.as_view(),name="bookmark_list")
]
