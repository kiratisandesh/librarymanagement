from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Book, StudentExtra, IssuedBook, Review

admin.site.unregister(User)
# Register with custom display
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    
admin.site.register(User, CustomUserAdmin)

# --- Update Book Admin to show new inventory fields ---
class BookAdmin(admin.ModelAdmin):
    list_display = ('name', 'isbn', 'author', 'category', 'total_copies', 'available_copies')
    list_filter = ('category',)
    search_fields = ('name', 'author', 'isbn')
    fields = ('name', 'isbn', 'author', 'category', 'total_copies', 'available_copies')

admin.site.register(Book, BookAdmin)


class StudentExtraAdmin(admin.ModelAdmin):
    pass
admin.site.register(StudentExtra, StudentExtraAdmin)


class IssuedBookAdmin(admin.ModelAdmin):
    pass
admin.site.register(IssuedBook, IssuedBookAdmin)


# ---Review Admin ---
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('book', 'user', 'rating', 'created_at', 'review_preview')
    list_filter = ('rating', 'created_at')
    search_fields = ('book__name', 'user__username', 'review_text')
    readonly_fields = ('book', 'user', 'rating', 'review_text', 'created_at')  # Make fields read-only
    
    # Show a preview of the review text in the list
    def review_preview(self, obj):
        if obj.review_text:
            return obj.review_text[:50] + '...' if len(obj.review_text) > 50 else obj.review_text
        return '-'
    review_preview.short_description = 'Review Preview'
    
    # Remove the "Add Review" button since admins shouldn't create reviews
    def has_add_permission(self, request):
        return False
    
    # Allow delete only
    def has_change_permission(self, request, obj=None):
        return False  # Can view but not edit

admin.site.register(Review, ReviewAdmin)