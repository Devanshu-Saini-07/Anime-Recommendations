from django.urls import path

from tracker import views

urlpatterns = [
    path("api/anime", views.anime_collection, name="api-anime"),
    path("api/anime/<int:anime_id>", views.anime_detail, name="api-anime-detail"),
    path("api/preferences", views.preferences, name="api-preferences"),
    path("api/recommendations", views.recommendations, name="api-recommendations"),
]
