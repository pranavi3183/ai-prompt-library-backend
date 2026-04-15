from django.urls import path
from .views import PromptListView, PromptDetailView, TagListView

urlpatterns = [
    path('prompts/', PromptListView.as_view()),
    path('prompts/<int:pk>/', PromptDetailView.as_view()),
    path('tags/', TagListView.as_view()),
]