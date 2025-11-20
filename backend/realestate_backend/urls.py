from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

def home(request):
    return JsonResponse({
        'message': 'Real Estate Analysis API is running!',
        'endpoints': {
            'analyze': '/api/analyze/',
            'admin': '/admin/'
        },
        'usage': 'Send POST requests to /api/analyze/ with JSON: {"query": "your query"}'
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('chatbot.urls')),
    path('', home),  # Add this line for root URL
]