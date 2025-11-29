from django.contrib import admin
from .models import Book,StudentExtra,IssuedBook
# Register your models here.

# --- Update Book Admin to show new inventory fields ---
class BookAdmin(admin.ModelAdmin):
    list_display = ('name', 'isbn', 'author', 'category', 'total_copies', 'available_copies')
    list_filter = ('category',)
    search_fields = ('name', 'author', 'isbn')
    
    # Allow editing both total_copies and available_copies
    fields = ('name', 'isbn', 'author', 'category', 'total_copies', 'available_copies')
    
    def save_model(self, request, obj, form, change):
        # If creating a new book, set available_copies to total_copies
        if not change:  # This means it's a new object
            obj.available_copies = obj.total_copies
        super().save_model(request, obj, form, change)

admin.site.register(Book, BookAdmin)

class StudentExtraAdmin(admin.ModelAdmin):
    pass
admin.site.register(StudentExtra, StudentExtraAdmin)


class IssuedBookAdmin(admin.ModelAdmin):
    pass
admin.site.register(IssuedBook, IssuedBookAdmin)

