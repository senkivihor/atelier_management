from django.contrib import admin
from .models import Task, TaskStatus

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'client', 'status', 'deadline', 'is_overdue', 'is_due_soon', 'created_at')
    list_filter = ('status', 'deadline', 'client')
    search_fields = ('title', 'description', 'client__first_name', 'client__last_name')
    date_hierarchy = 'created_at' # Adds date navigation
    readonly_fields = ('created_at', 'updated_at', 'completed_at')
    fieldsets = (
        (None, {
            'fields': ('client', 'title', 'description')
        }),
        ('Status & Deadlines', {
            'fields': ('status', 'deadline', 'completed_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    # Custom actions for Admin (example)
    @admin.action(description="Mark selected tasks as 'In Progress'")
    def mark_in_progress(self, request, queryset):
        updated_count = queryset.filter(status=TaskStatus.PENDING).update(status=TaskStatus.IN_PROGRESS)
        self.message_user(request, f"{updated_count} tasks marked as 'In Progress'.")

    @admin.action(description="Mark selected tasks as 'Completed'")
    def mark_completed(self, request, queryset):
        # When marking completed, the save() method will set completed_at
        updated_count = 0
        for task in queryset.filter(status__in=[TaskStatus.PENDING, TaskStatus.IN_PROGRESS, TaskStatus.ON_HOLD]):
            task.status = TaskStatus.COMPLETED
            task.save() # Call save() to trigger the custom logic
            updated_count += 1
        self.message_user(request, f"{updated_count} tasks marked as 'Completed'.")

    actions = [mark_in_progress, mark_completed] # Register custom actions
    