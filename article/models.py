from django.db import models
from django.utils import timezone
from accounts.models import Profile

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=255,unique=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "categories"

class Article(models.Model):
    category = models.ForeignKey(Category,on_delete=models.SET_NULL,null=True,related_name="articles")
    title = models.CharField(max_length=1000)
    description = models.TextField()
    cover_image = models.ImageField(upload_to="Article/Cover/",null=True,blank=True)
    read_min = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True,blank=True)
    is_top = models.BooleanField(default=False)
    is_trending = models.BooleanField(default=False)
    bookmark = models.ManyToManyField(Profile,blank=True,related_name="bookmarked_articles")
    likes = models.ManyToManyField(Profile,blank=True,related_name="liked_articles")

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if self.is_published :
            if not self.published_at:
                self.published_at = timezone.now()
        else:
            self.published_at = None
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["-published_at"]

class Paragraph(models.Model):
    article = models.ForeignKey(Article,on_delete=models.CASCADE,related_name="paragraph")
    heading = models.CharField(max_length=1000)
    description = models.TextField(blank=True,null=True)
    index = models.PositiveIntegerField()

    def __str__(self):
        return self.heading
    
    class Meta:
        ordering = ["index"]
    
class Comment(models.Model):
    profile = models.ForeignKey(Profile,on_delete=models.CASCADE)
    article = models.ForeignKey(Article,on_delete=models.CASCADE,related_name="comments")
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.profile.name} - {self.article.title}"
    
    class Meta:
        ordering = ["-created_at"]