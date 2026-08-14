import random
import string
from django.shortcuts import render

def conversation_home(request):
    # Generate a random 6-character room code
    room_name = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return render(request, 'conversation/home.html', {'room_name': room_name})

def conversation_room(request, room_name):
    return render(request, 'conversation/room.html', {'room_name': room_name})
