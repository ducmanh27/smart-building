from django.urls import path
from api import views
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

urlpatterns = [
    path('room/set_timer', views.setTimerActuator),
    path('v1.1/monitor/data', views.getSensorSecondlyData),
    path('v1.1/monitor/data/history', views.historyChart),
    # path('room/kriging', views.kriging),
    path('v1.1/control/fans',views.send_setpoint), #view to send setpoint to gateway
    path('get/token_auth', obtain_auth_token), #api to get token authentication
    # path('token', TokenObtainPairView.as_view()),
    path('token', views.CustomTokeObtainPairview.as_view()),
    path('token/refresh', TokenRefreshView.as_view()),
    path('token/verify', TokenVerifyView.as_view()),
    path('room', views.getRoomData),    #!< api for getting room data for langingPage component on frontend
    path('room/information_tag', views.getRoomInformationTag),  #!< api for InformationTag component
    path('room/AQIdustpm2_5', views.AQIdustpm2_5),  #!< api for InformationTag component
    path('actuator_status', views.getActuatorStatus),
    path('actuator_command', views.setActuator),
    path('configuration/room/all', views.getConfigurationRoomAll),  #!< api for InformationTag component
    path('configuration/room/command', views.configurationRoom),  #!< api for InformationTag component
    path('configuration/node/command', views.configurationNode),  #!< api for InformationTag component
    path('aqi_ref', views.getAqiRef),  #!< api for AqiRef component
    path('weatherdata', views.getWeatherdata),  #!< api for Weatherdata component
    path('signup', views.signUp),
    path('energydata/realtime/monitor',views.EnergyDataAPIView.as_view()),
    path('energydata/monitor',views.EnergyDataChartAPIView.as_view()),
    path('heatmap', views.HeatMapData.as_view())
    #______________________________________________________
]
