from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile

# Define an inline admin descriptor for UserProfile model
# which can be used in UserAdmin
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'profile'
    fieldsets = (
        (None, {
            'fields': ('role', 'phone_number')
        }),
    )

# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_role')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups', 'profile__role')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'profile__phone_number')

    # Correct way to modify fieldsets to avoid duplication
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    def get_role(self, obj):
        return obj.profile.get_role_display()
    get_role.short_description = 'Role'
    get_role.admin_order_field = 'profile__role'

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
