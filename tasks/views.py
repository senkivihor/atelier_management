from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.contrib import messages
from .models import Task, TaskStatus
from .forms import TaskForm # Create this in next step

class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'tasks/task_list.html'
    context_object_name = 'tasks'
    paginate_by = 10

    def get_queryset(self):
        # Example of using custom manager methods
        queryset = super().get_queryset()
        status_filter = self.request.GET.get('status')
        client_filter = self.request.GET.get('client')

        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if client_filter:
            queryset = queryset.filter(client_id=client_filter)

        return queryset.select_related('client') # Optimize query for client data

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['task_statuses'] = TaskStatus.choices # Pass choices to template for filter dropdown
        from clients.models import Client # Import here to avoid circular dependency at top
        context['clients'] = Client.objects.all().order_by('first_name')
        return context

class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    template_name = 'tasks/task_detail.html'
    context_object_name = 'task'

class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = 'tasks/partials/task_form.html'
    success_url = reverse_lazy('task_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Task '{self.object.title}' created successfully!")
        if self.request.htmx:
            tasks = self.get_queryset() # Use get_queryset to apply filters if any
            html = render_to_string('tasks/partials/task_table.html', {'tasks': tasks}, request=self.request)
            return HttpResponse(html, headers={'HX-Trigger': 'taskCreated'})
        return response

    def form_invalid(self, form):
        response = super().form_invalid(form)
        if self.request.htmx:
            return self.render_to_response(self.get_context_data(form=form))
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_create'] = True
        return context

class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = 'tasks/partials/task_form.html'
    success_url = reverse_lazy('task_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Task '{self.object.title}' updated successfully!")
        if self.request.htmx:
            html = render_to_string('tasks/partials/task_row.html', {'task': self.object}, request=self.request)
            return HttpResponse(html, headers={'HX-Trigger': 'taskUpdated'})
        return response

    def form_invalid(self, form):
        response = super().form_invalid(form)
        if self.request.htmx:
            return self.render_to_response(self.get_context_data(form=form))
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_update'] = True
        return context

class TaskDeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    success_url = reverse_lazy('task_list')

    def post(self, request, *args, **kwargs):
        messages.success(self.request, f"Task '{self.get_object().title}' deleted successfully!")
        response = super().post(request, *args, **kwargs)
        if self.request.htmx:
            return HttpResponse(status=204)
        return response

    def get(self, request, *args, **kwargs):
        if request.htmx:
            return super().get(request, *args, **kwargs)
        messages.error(self.request, "Direct access to delete page not allowed.")
        return redirect('task_list')

class TaskStatusUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    fields = ['status'] # Only allow updating status
    http_method_names = ['post'] # Only allow POST requests for this

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Task '{self.object.title}' status updated to '{self.object.get_status_display()}'!")
        if self.request.htmx:
            # Return the updated task detail partial for the detail page
            # or just the row for the list view if triggered there
            html = render_to_string('tasks/partials/task_detail_card.html', {'task': self.object}, request=self.request)
            return HttpResponse(html, headers={'HX-Trigger': 'taskStatusUpdated'})
        return response

    def form_invalid(self, form):
        response = super().form_invalid(form)
        if self.request.htmx:
            return HttpResponse(f"<div class='error'>Error updating status: {form.errors}</div>", status=400)
        return response
    