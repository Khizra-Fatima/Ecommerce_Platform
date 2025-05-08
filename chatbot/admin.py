from django.contrib import admin
from .models import Keyword, ChatBotIntent, ChatBotResponse

admin.site.register(ChatBotIntent)
admin.site.register(ChatBotResponse)
admin.site.register(Keyword)