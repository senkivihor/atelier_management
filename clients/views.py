from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import HttpResponse # For HTMX partial responses
from django.template.loader import render_to_string
from django.contrib import messages # For Django messages
from .models import Client
from .forms import ClientForm

class ClientListView(LoginRequiredMixin, ListView):
    """
    Displays a list of all clients.
    Uses Django's ListView CBV.
    """
    model = Client
    template_name = 'clients/client_list.html'
    context_object_name = 'clients'
    paginate_by = 10 # Optional: pagination

class ClientDetailView(LoginRequiredMixin, DetailView):
    """
    Displays the details of a single client.
    Uses Django's DetailView CBV.
    """
    model = Client
    template_name = 'clients/client_detail.html'
    context_object_name = 'client'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Fetch tasks related to this client
        context['tasks'] = self.object.tasks.all().order_by('-created_at')
        return context

class ClientCreateView(LoginRequiredMixin, CreateView):
    model = Client
    form_class = ClientForm
    template_name = 'clients/partials/client_form.html' # Use a partial template for modal
    success_url = reverse_lazy('client_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Client '{self.object.get_full_name()}' created successfully!")
        # For HTMX, respond with the updated list or a success message
        if self.request.htmx:
            # Reload the client list dynamically
            clients = Client.objects.all()
            html = render_to_string('clients/partials/client_table.html', {'clients': clients}, request=self.request)
            return HttpResponse(html)
        return response

    def form_invalid(self, form):
        response = super().form_invalid(form)
        if self.request.htmx:
            # Return the form with errors for HTMX to re-render the modal
            return self.render_to_response(self.get_context_data(form=form))
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_create'] = True
        return context

class ClientUpdateView(LoginRequiredMixin, UpdateView):
    model = Client
    form_class = ClientForm
    template_name = 'clients/partials/client_form.html' # Use partial template
    success_url = reverse_lazy('client_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Client '{self.object.get_full_name()}' updated successfully!")
        if self.request.htmx:
            # Return the updated row or refresh the list
            html = render_to_string('clients/partials/client_row.html', {'client': self.object}, request=self.request)
            return HttpResponse(html, headers={'HX-Trigger': 'clientUpdated'}) # HX-Trigger for specific updates
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

class ClientDeleteView(LoginRequiredMixin, DeleteView):
    model = Client
    success_url = reverse_lazy('client_list')

    def post(self, request, *args, **kwargs):
        messages.success(self.request, f"Client '{self.get_object().get_full_name()}' deleted successfully!")
        response = super().post(request, *args, **kwargs)
        if self.request.htmx:
            # HTMX expects a 200 OK or 204 No Content for successful deletion of target.
            # If we want to remove the row, 204 is appropriate.
            return HttpResponse(status=204) # No content to return, just remove element
        return response

    # A dummy get method to prevent direct access to delete page if not HTMX
    def get(self, request, *args, **kwargs):
        if request.htmx:
            return super().get(request, *args, **kwargs)
        # You might want to redirect to a confirmation page or raise Http404
        messages.error(self.request, "Direct access to delete page not allowed.")
        return redirect('client_list') # Or render a confirmation page