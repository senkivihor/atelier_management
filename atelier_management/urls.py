# atelier_management/atelier_management/urls.py
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views # Import Django's auth views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/login/'), name='logout'), # Redirect to login after logout
    # Add client/task URLs here later
    path('', include('clients.urls')), # Include client app URLs
    path('', include('tasks.urls')),   # Include task app URLs
    path('', include('users.urls')),   # Include user app URLs (for dashboard)
]