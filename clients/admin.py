from django.contrib import admin
from .models import Client

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'email', 'phone_number', 'created_at')
    search_fields = ('first_name', 'last_name', 'email', 'phone_number')
    list_filter = ('created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at') # Ensure these aren't editable
    fieldsets = (
        (None, {
            'fields': ('first_name', 'last_name', 'email', 'phone_number')
        }),
        ('Additional Information', {
            'fields': ('address', 'notes'),
            'classes': ('collapse',) # Makes this section collapsible
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    