from django.contrib import admin
from .models import Category , Article , Paragraph , Comment

# Register your models here.

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug":("name",)}

class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0

class ParagraphInline(admin.TabularInline):
    model = Paragraph
    extra = 0

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    inlines = [ParagraphInline,CommentInline]
    list_display = ["title","id","is_published","published_at"]
    search_fields = ["title","category__name"]
    list_filter = ["category","is_top","is_published"]