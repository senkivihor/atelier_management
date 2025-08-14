from django.urls import path
from .views import DashboardView # Will add later for DashboardView

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('', DashboardView.as_view(), name='home'), # Make dashboard the home page
]
