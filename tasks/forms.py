from django import forms
from .models import Task

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['client', 'title', 'description', 'status', 'deadline']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'deadline': forms.DateInput(attrs={'type': 'date'}), # HTML5 date input
        }

    # Override __init__ to dynamically set client queryset if needed (e.g., for employee scope)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['client'].queryset = self.fields['client'].queryset.order_by('first_name', 'last_name')
        