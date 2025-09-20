# blog/admin.py

from django.contrib import admin
from .models import Post, Category, Tag, Comment
from users.models import CustomUser

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'get_author', 'created_at', 'updated_at')
    list_filter = ('created_at', 'categories', 'tags')
    search_fields = ('title', 'content')
    filter_horizontal = ('categories', 'tags')

    def get_author(self, obj):
        # Fetch the author from the 'credentials' database
        if obj.author_id:
            try:
                user = CustomUser.objects.using('credentials').get(pk=obj.author_id)
                return user.username
            except CustomUser.DoesNotExist:
                return "N/A"
        return "N/A"
    get_author.short_description = 'Author'

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('get_author_username', 'post_title','text', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('post__title', 'text')

    def get_queryset(self, request):
        # Start with the base queryset from the correct database
        qs = super().get_queryset(request).using('default').select_related('post')
        
        # Get a list of unique author IDs from the comments
        author_ids = list(qs.values_list('author_id', flat=True).distinct())
        
        # Fetch all related author objects in a single query from the 'credentials' db
        authors = CustomUser.objects.using('credentials').filter(pk__in=author_ids)
        
        # Create a dictionary for easy lookup: {author_id: author_username}
        author_map = {author.pk: author.username for author in authors}
        
        # Attach the author's username to each comment object
        for comment in qs:
            comment.author_username = author_map.get(comment.author_id, "N/A")
            
        return qs

    def get_author_username(self, obj):
        return getattr(obj, 'author_username', "N/A")
    get_author_username.short_description = 'Author'
    get_author_username.admin_order_field = 'author_id'

    def post_title(self, obj):
        return obj.post.title
    post_title.short_description = 'Post'
    post_title.admin_order_field = 'post__title'