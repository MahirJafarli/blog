from django.contrib import admin
from .models import Category, Tag, Post, Comment


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Admin configuration for Category model.
    """
    list_display = ['name', 'slug', 'created_date', 'post_count']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_date']
    
    def post_count(self, obj):
        """Display number of posts in this category."""
        return obj.posts.count()
    post_count.short_description = 'Number of Posts'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """
    Admin configuration for Tag model.
    """
    list_display = ['name', 'slug', 'created_date', 'post_count']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_date']
    
    def post_count(self, obj):
        """Display number of posts with this tag."""
        return obj.posts.count()
    post_count.short_description = 'Number of Posts'


class CommentInline(admin.TabularInline):
    """
    Inline admin for displaying comments within Post admin.
    """
    model = Comment
    extra = 1
    fields = ['author', 'content', 'is_approved', 'created_date']
    readonly_fields = ['created_date']
    raw_id_fields = ['author']


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """
    Admin configuration for Post model.
    Includes inline comments and advanced features.
    """
    list_display = ['title', 'author', 'status', 'published_date', 'created_date', 'comment_count']
    list_filter = ['author', 'status', 'created_date', 'published_date', 'categories']
    search_fields = ['title', 'content', 'author__username']
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ['author']
    date_hierarchy = 'published_date'
    ordering = ['-published_date', '-created_date']
    filter_horizontal = ['categories', 'tags']
    readonly_fields = ['created_date', 'updated_date']
    inlines = [CommentInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'author', 'excerpt')
        }),
        ('Content', {
            'fields': ('content',)
        }),
        ('Relationships', {
            'fields': ('categories', 'tags'),
            'classes': ('collapse',),
        }),
        ('Publishing', {
            'fields': ('status', 'published_date')
        }),
        ('Metadata', {
            'fields': ('created_date', 'updated_date'),
            'classes': ('collapse',),
        }),
    )
    
    def comment_count(self, obj):
        """Display number of comments on this post."""
        return obj.comments.count()
    comment_count.short_description = 'Comments'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """
    Admin configuration for Comment model.
    """
    list_display = ['post', 'author', 'content_preview', 'is_approved', 'created_date']
    list_filter = ['is_approved', 'created_date']
    search_fields = ['content', 'author__username', 'post__title']
    raw_id_fields = ['post', 'author']
    readonly_fields = ['created_date', 'updated_date']
    date_hierarchy = 'created_date'
    actions = ['approve_comments', 'unapprove_comments']
    
    def content_preview(self, obj):
        """Show first 50 characters of content."""
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'
    
    def approve_comments(self, request, queryset):
        """Bulk approve selected comments."""
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'{updated} comments approved.')
    approve_comments.short_description = 'Approve selected comments'
    
    def unapprove_comments(self, request, queryset):
        """Bulk unapprove selected comments."""
        updated = queryset.update(is_approved=False)
        self.message_user(request, f'{updated} comments unapproved.')
    unapprove_comments.short_description = 'Unapprove selected comments'