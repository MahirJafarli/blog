from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from .models import Post


def home(request):
    """
    Project-level home view.
    Demonstrates XSS protection with auto-escaping.
    """
    context = {
        'user_input': '<script>alert("XSS Attack!")</script>',
    }
    return render(request, 'home.html', context)


def post_list(request):
    """
    Blog post list view with pagination and search.
    
    Features:
    - Pagination: 10 posts per page
    - Search: Search in title, content, and author username
    - Query optimization: select_related and prefetch_related
    
    URL parameters:
    - page: Page number (default: 1)
    - q: Search query (optional)
    """
    # Get search query from URL parameters
    search_query = request.GET.get('q', '')
    
    # Base queryset: all published posts
    posts = Post.objects.filter(status='published')
    
    # Apply search filter if search query exists
    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query) |
            Q(author__username__icontains=search_query) |
            Q(categories__name__icontains=search_query) |
            Q(tags__name__icontains=search_query)
        ).distinct()
    
    # Optimize queries
    posts = posts.select_related('author').prefetch_related('categories', 'tags')
    
    # Order posts
    posts = posts.order_by('-published_date')
    
    # Pagination: 10 posts per page
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page
        page_obj = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver last page
        page_obj = paginator.page(paginator.num_pages)
    
    context = {
        'posts': page_obj,
        'page_obj': page_obj,
        'search_query': search_query,
    }
    return render(request, 'blog/blog_list.html', context)


def post_detail(request, slug):
    """
    Blog post detail view.
    Displays a single post with all its details including comments.
    """
    post = get_object_or_404(
        Post.objects.select_related('author').prefetch_related(
            'categories',
            'tags',
            'comments__author'
        ),
        slug=slug,
        status='published'
    )
    
    context = {'post': post}
    return render(request, 'blog/blog_detail.html', context)