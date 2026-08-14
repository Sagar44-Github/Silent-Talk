from django.urls import path
from . import views

urlpatterns = [
    path("",                  views.conversation_home, name="conversation_home"),
    path("<str:room_name>/",  views.conversation_room, name="conversation_room"),
]
