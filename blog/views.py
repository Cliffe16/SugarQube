from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Post, Tag
from .forms import CommentForm

def blog_home(request):
    # Get all posts initially
    posts = Post.objects.all()
    
    # Get all tags for the sidebar
    all_tags = Tag.objects.all()
    
    # Filtering Logic 
    tag_filter = request.GET.get('tag')
    if tag_filter:
        posts = posts.filter(tags__name=tag_filter)
        
    # Sorting Logic 
    sort_by = request.GET.get('sort', '-created_at') # Default to newest
    valid_sort_fields = ['created_at', '-created_at', 'title', '-title']
    if sort_by not in valid_sort_fields:
        sort_by = '-created_at' # Default if invalid sort is provided
        
    posts = posts.order_by(sort_by)

    context = {
        'posts': posts,
        'all_tags': all_tags,
        'current_sort': sort_by,
        'current_tag': tag_filter,
    }
    return render(request, 'blog/blog_home.html', context)

def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    comment_form = CommentForm()

    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to comment.")
            return redirect('login')

        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.author = request.user
            new_comment.save()
            messages.success(request, "Your comment has been added successfully.")
            return redirect('post_detail', pk=post.pk)
    
    context = {
        'post': post,
        'comments': post.comments.order_by('-created_at'),
        'comment_form': comment_form
    }
    return render(request, 'blog/post_detail.html', context)