from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserRole(models.TextChoices):
    ADMIN = 'admin', 'Administrator'
    EMPLOYEE = 'employee', 'Employee'

class UserProfile(models.Model):
    """
    Extends the built-in Django User model with additional profile information,
    specifically a role. This follows the Proxy Pattern (indirectly) by adding behavior
    to an existing model without modifying its structure, and OCP for extensibility.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.EMPLOYEE,
        help_text="The role of the user within the atelier."
    )
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    # Add other fields specific to your atelier staff if needed
    # e.g., 'specialization', 'hire_date'

    def __str__(self):
        return f"{self.user.username}'s Profile ({self.get_role_display()})"

# Signal receivers to automatically create/update UserProfile when a User is created/saved
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Signal handler to automatically create or update a UserProfile whenever a User is saved.
    This demonstrates an application of the Observer pattern.
    """
    if created:
        UserProfile.objects.create(user=instance)
    instance.profile.save() # Ensure profile is always saved/updated
    