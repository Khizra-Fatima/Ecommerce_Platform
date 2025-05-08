from django.db import models


class Keyword(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        verbose_name_plural = "Keywords"

    def __str__(self):
        return self.name



class ChatBotIntent(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    keywords = models.ManyToManyField(Keyword, related_name="intents")

    def __str__(self):
        return self.name



class ChatBotResponse(models.Model):
    intent = models.ForeignKey(ChatBotIntent, on_delete=models.CASCADE)
    response_text = models.TextField()
    dynamic = models.BooleanField(default=False)


    def __str__(self):
        return f"Response for intent: {self.intent.name}"