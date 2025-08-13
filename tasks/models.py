from django.db import models
from django.utils import timezone
from clients.models import Client # Import the Client model

# Strategy Pattern (Implicit): Using different status choices to alter behavior.
class TaskStatus(models.TextChoices):
    """
    Defines choices for task status.
    Encapsulates task status options, adhering to Open/Closed Principle (OCP)
    if new statuses are added, they can be added here without modifying core logic
    that uses these choices (as long as the usage is generic).
    """
    PENDING = 'pending', 'Pending'
    IN_PROGRESS = 'in_progress', 'In Progress'
    ON_HOLD = 'on_hold', 'On Hold'
    COMPLETED = 'completed', 'Completed'
    CANCELLED = 'cancelled', 'Cancelled'

class TaskQuerySet(models.QuerySet):
    """
    Custom QuerySet for Task model.
    Extends default manager with specific business logic queries.
    This follows the Repository Pattern idea of encapsulating query logic.
    """
    def get_tasks_near_deadline(self, days=3):
        """Returns tasks that are not completed/cancelled and are due within 'days'."""
        today = timezone.localdate()
        due_date_limit = today + timezone.timedelta(days=days)
        return self.filter(
            deadline__gte=today,
            deadline__lte=due_date_limit,
            status__in=[TaskStatus.PENDING, TaskStatus.IN_PROGRESS, TaskStatus.ON_HOLD]
        ).order_by('deadline')

    def get_overdue_tasks(self):
        """Returns tasks that are not completed/cancelled and are past their deadline."""
        today = timezone.localdate()
        return self.filter(
            deadline__lt=today,
            status__in=[TaskStatus.PENDING, TaskStatus.IN_PROGRESS, TaskStatus.ON_HOLD]
        ).order_by('deadline')

    def get_active_tasks(self):
        """Returns tasks that are not completed or cancelled."""
        return self.exclude(status__in=[TaskStatus.COMPLETED, TaskStatus.CANCELLED])

    def get_completed_tasks_this_month(self):
        """Returns tasks completed in the current month."""
        now = timezone.now()
        return self.filter(
            status=TaskStatus.COMPLETED,
            completed_at__year=now.year,
            completed_at__month=now.month
        )

class Task(models.Model):
    """
    Represents a work task for the atelier.
    Adheres to Single Responsibility Principle (SRP) for task data.
    """
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE, # If client is deleted, tasks are deleted.
        related_name='tasks', # Allows client.tasks.all()
        help_text="The client associated with this task."
    )
    title = models.CharField(max_length=255, help_text="A brief title for the task.")
    description = models.TextField(blank=True, help_text="Detailed description of the work to be done.")
    status = models.CharField(
        max_length=20,
        choices=TaskStatus.choices,
        default=TaskStatus.PENDING,
        help_text="Current status of the task."
    )
    deadline = models.DateField(
        null=True,
        blank=True,
        help_text="The date by which the task should be completed."
    )
    # Using a separate field for completion date for reporting
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date and time when the task was marked as completed."
    )
    created_at = models.DateTimeField(auto_now_add=True, help_text="Date and time when the task was created.")
    updated_at = models.DateTimeField(auto_now=True, help_text="Last date and time when the task was updated.")

    # Assign our custom manager
    objects = TaskQuerySet.as_manager()

    class Meta:
        verbose_name = "Task"
        verbose_name_plural = "Tasks"
        ordering = ['-created_at'] # Order by most recent first

    def __str__(self):
        return f"Task: {self.title} for {self.client.get_full_name()} ({self.status})"

    def save(self, *args, **kwargs):
        """
        Override save method to set completed_at when status changes to COMPLETED.
        This demonstrates a simple application of the Observer pattern (implicitly,
        as the model 'observes' its own status change).
        """
        if self.pk: # Only on existing instances
            original = Task.objects.get(pk=self.pk)
            if original.status != TaskStatus.COMPLETED and self.status == TaskStatus.COMPLETED:
                self.completed_at = timezone.now()
            elif original.status == TaskStatus.COMPLETED and self.status != TaskStatus.COMPLETED:
                self.completed_at = None # If status changes from completed, clear completion date
        super().save(*args, **kwargs)

    @property
    def is_overdue(self):
        """Checks if the task is overdue."""
        if self.deadline and self.status not in [TaskStatus.COMPLETED, TaskStatus.CANCELLED]:
            return self.deadline < timezone.localdate()
        return False

    @property
    def is_due_soon(self):
        """Checks if the task is due soon (e.g., within 3 days)."""
        if self.deadline and self.status not in [TaskStatus.COMPLETED, TaskStatus.CANCELLED]:
            return timezone.localdate() <= self.deadline <= (timezone.localdate() + timezone.timedelta(days=3))
        return False
    