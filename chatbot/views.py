from django.shortcuts import render
from django.http import JsonResponse
from .models import Keyword, ChatBotIntent, ChatBotResponse


def get_chatbot_response(request):
    user_query = request.GET.get('query', '').lower().strip()

    if not user_query:
        return JsonResponse({'response': "I didn't understand that. Could you please try again?"})

    # Match keywords
    matched_keywords = Keyword.objects.filter(name__icontains=user_query)
    if matched_keywords.exists():
        # Get intents for matched keywords
        intents = ChatBotIntent.objects.filter(keywords__in=matched_keywords).distinct()

        if intents.exists():
            # Get the first matched intent and response
            intent = intents.first()
            response = ChatBotResponse.objects.filter(intent=intent, dynamic=False).first()
            if response:
                return JsonResponse({'response': response.response_text})

    # Fallback response
    return JsonResponse({
        'response': "Sorry, I couldn't find an answer to that. You can contact our support team for further assistance:\n\n"
                    "Email: support@ourplatform\n"
                    "Phone: +1-800-555-1234"
    })


