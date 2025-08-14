import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Task, TaskStatus

class DashboardConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Only allow authenticated users to connect to the dashboard websocket
        if not self.scope["user"].is_authenticated:
            await self.close()
            return

        self.dashboard_group_name = 'dashboard_updates'

        # Join group
        await self.channel_layer.group_add(
            self.dashboard_group_name,
            self.channel_name
        )

        await self.accept()
        # Send initial data when connected
        await self.send_dashboard_data()

    async def disconnect(self, close_code):
        # Leave group
        await self.channel_layer.group_discard(
            self.dashboard_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # We don't expect messages from the client for this dashboard
        pass

    async def send_dashboard_data(self):
        """
        Fetches current dashboard data and sends it to the connected client.
        """
        data = await self.get_dashboard_metrics()
        await self.send(text_data=json.dumps({
            'type': 'dashboard_metrics',
            'data': data
        }))

    @sync_to_async
    def get_dashboard_metrics(self):
        """
        Synchronous function to fetch metrics from the database.
        Runs in a thread pool managed by Channels.
        """
        overdue_tasks = Task.objects.get_overdue_tasks().count()
        due_soon_tasks = Task.objects.get_tasks_near_deadline(days=3).count()
        in_progress_tasks = Task.objects.filter(status=TaskStatus.IN_PROGRESS).count()
        pending_tasks = Task.objects.filter(status=TaskStatus.PENDING).count()
        completed_this_month = Task.objects.get_completed_tasks_this_month().count()

        return {
            'overdue_count': overdue_tasks,
            'due_soon_count': due_soon_tasks,
            'in_progress_count': in_progress_tasks,
            'pending_count': pending_tasks,
            'completed_this_month_count': completed_this_month,
        }

    # Receive message from channel layer group
    async def dashboard_message(self, event):
        """
        Called when a message is received from the 'dashboard_updates' group.
        """
        await self.send_dashboard_data()

# Signal handlers to send updates to the dashboard group
@receiver(post_save, sender=Task)
@receiver(post_delete, sender=Task)
def task_changed_handler(sender, instance, **kwargs):
    """
    Signal handler to notify dashboard group when a Task is saved or deleted.
    This sends a message to the channel layer, which then broadcasts to connected consumers.
    """
    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'dashboard_updates',
        {
            'type': 'dashboard.message', # This calls the dashboard_message method in the consumer
        }
    )
    