from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from tasks.models import Task, TaskStatus # Import Task and TaskStatus

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'users/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Initial data for the dashboard. Real-time updates will come via WebSocket.
        context['overdue_tasks'] = Task.objects.get_overdue_tasks()
        context['due_soon_tasks'] = Task.objects.get_tasks_near_deadline(days=3)
        context['in_progress_tasks'] = Task.objects.filter(status=TaskStatus.IN_PROGRESS)
        context['pending_tasks'] = Task.objects.filter(status=TaskStatus.PENDING)
        context['completed_this_month_count'] = Task.objects.get_completed_tasks_this_month().count()
        return context
    