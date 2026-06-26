from django.urls import path
from .views import CypherpunkGameView

app_name = "cypherpunkgame"
urlpatterns = [
    path("", CypherpunkGameView.as_view(), name="dispatch"),
]
