from django.urls import re_path
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack # For authentication in websockets
from tasks.consumers import DashboardConsumer # Will create this next

application = ProtocolTypeRouter({
    "websocket": AuthMiddlewareStack(
        URLRouter([
            re_path(r"ws/dashboard/$", DashboardConsumer.as_asgi()),
        ])
    ),
})
