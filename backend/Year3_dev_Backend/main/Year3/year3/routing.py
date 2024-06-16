# from channels.routing import ProtocolTypeRouter, URLRouter
# from channels.security.websocket import AllowedHostsOriginValidator
# from django.urls import path
# from api.consumers import TokenAuthConsumer
# from api.middlewares import TokenAuthMiddleWare


# print("COME IN HEREEEEEEEEEEEEEEEEEEEEEEEEEEe!")

# application = ProtocolTypeRouter(
# 	{
# 		"websocket": TokenAuthMiddleWare(
# 			AllowedHostsOriginValidator(
# 				URLRouter(
# 				[path("", TokenAuthConsumer.as_asgi())]
# 				)
# 			)
# 		)
# 	}
# )
