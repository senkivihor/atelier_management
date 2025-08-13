from django.db import models
from django.utils import timezone

class Client(models.Model):
    """
    Represents a client of the atelier.
    Adheres to Single Responsibility Principle (SRP) for client data.
    """
    first_name = models.CharField(max_length=100, help_text="Client's first name.")
    last_name = models.CharField(max_length=100, help_text="Client's last name.")
    email = models.EmailField(
        max_length=255,
        unique=True,
        null=True,
        blank=True,
        help_text="Client's email address (optional, but recommended for communication)."
    )
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        help_text="Client's phone number for contact."
    )
    address = models.TextField(
        blank=True,
        help_text="Full address of the client."
    )
    notes = models.TextField(
        blank=True,
        help_text="Any additional notes about the client (e.g., preferences)."
    )
    created_at = models.DateTimeField(auto_now_add=True, help_text="Date and time when the client profile was created.")
    updated_at = models.DateTimeField(auto_now=True, help_text="Last date and time when the client profile was updated.")

    class Meta:
        verbose_name = "Client"
        verbose_name_plural = "Clients"
        ordering = ['last_name', 'first_name']

    def __str__(self):
        """
        String representation of the client, useful for admin and debugging.
        """
        return f"{self.first_name} {self.last_name}"

    def get_full_name(self):
        """
        Returns the client's full name.
        """
        return f"{self.first_name} {self.last_name}"

    # Potential future methods related to client-specific actions
    # def get_active_tasks(self):
    #     return self.tasks.filter(status__in=['pending', 'in_progress'])

    # Example of a property for computed value
    @property
    def contact_info(self):
        """Returns primary contact info."""
        return self.email if self.email else self.phone_number
    