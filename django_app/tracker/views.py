import requests

from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .authentication import ExistingUserBasicAuthentication
from .models import Anime, AnimeCatalog, UserPreference

JIKAN_URL = "https://api.jikan.moe/v4/anime"
JIKAN_TIMEOUT = 5
STATUS_OPTIONS = {"Watching", "Completed", "Plan to Watch"}


def anime_to_dict(anime):
    return {
        "anime_id": anime.anime_id,
        "title": anime.title,
        "genre": anime.genre or "Unknown Genre",
        "status": anime.status or "Plan to Watch",
        "total_episodes": anime.total_episodes or 0,
        "description": anime.description or "",
        "poster_hint": anime.poster_hint or anime.genre or "Anime",
        "poster_url": anime.poster_url,
    }


def fetch_poster(title):
    try:
        response = requests.get(
            JIKAN_URL,
            params={"q": title, "limit": 1, "sfw": True},
            timeout=JIKAN_TIMEOUT,
        )
        response.raise_for_status()
        data = response.json().get("data") or []
        if not data:
            return None
        images = data[0].get("images") or {}
        jpg = images.get("jpg") or {}
        return jpg.get("large_image_url") or jpg.get("image_url")
    except requests.RequestException:
        return None


@api_view(["GET", "POST"])
@authentication_classes([ExistingUserBasicAuthentication])
@permission_classes([IsAuthenticated])
def anime_collection(request):
    if request.method == "GET":
        status_filter = request.query_params.get("status")
        queryset = Anime.objects.filter(user=request.user)
        if status_filter in STATUS_OPTIONS:
            queryset = queryset.filter(status=status_filter)
        return Response({"count": queryset.count(), "results": [anime_to_dict(a) for a in queryset]})

    payload = request.data
    title = str(payload.get("title", "")).strip()
    genre = str(payload.get("genre", "")).strip() or "Unknown Genre"
    anime_status = str(payload.get("status", "Plan to Watch")).strip()

    if not title:
        return Response({"detail": "title is required"}, status=status.HTTP_400_BAD_REQUEST)
    if anime_status not in STATUS_OPTIONS:
        return Response({"detail": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        total_episodes = max(int(payload.get("total_episodes", 0)), 0)
    except (TypeError, ValueError):
        return Response({"detail": "total_episodes must be an integer"}, status=status.HTTP_400_BAD_REQUEST)

    poster_url = fetch_poster(title)
    anime = Anime.objects.create(
        user=request.user,
        title=title,
        genre=genre,
        status=anime_status,
        total_episodes=total_episodes,
        description=str(payload.get("description", "")).strip(),
        poster_hint=genre,
        poster_url=poster_url,
    )
    return Response(anime_to_dict(anime), status=status.HTTP_201_CREATED)


@api_view(["GET", "PUT", "PATCH", "DELETE"])
@authentication_classes([ExistingUserBasicAuthentication])
@permission_classes([IsAuthenticated])
def anime_detail(request, anime_id):
    anime = Anime.objects.filter(anime_id=anime_id, user=request.user).first()
    if anime is None:
        return Response({"detail": "Anime not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        return Response(anime_to_dict(anime))

    if request.method == "DELETE":
        anime.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    payload = request.data
    if "title" in payload:
        title = str(payload["title"]).strip()
        if title:
            anime.title = title
    if "genre" in payload:
        anime.genre = str(payload["genre"]).strip() or anime.genre
    if "status" in payload:
        new_status = str(payload["status"]).strip()
        if new_status not in STATUS_OPTIONS:
            return Response({"detail": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)
        anime.status = new_status
    if "total_episodes" in payload:
        try:
            anime.total_episodes = max(int(payload["total_episodes"]), 0)
        except (TypeError, ValueError):
            return Response({"detail": "total_episodes must be an integer"}, status=status.HTTP_400_BAD_REQUEST)
    if "description" in payload:
        anime.description = str(payload["description"]).strip()

    anime.save()
    return Response(anime_to_dict(anime))


@api_view(["GET", "POST"])
@authentication_classes([ExistingUserBasicAuthentication])
@permission_classes([IsAuthenticated])
def preferences(request):
    if request.method == "GET":
        genres = list(
            UserPreference.objects.filter(user=request.user)
            .values_list("genre_name", flat=True)
            .order_by("genre_name")
        )
        return Response({"genres": genres})

    genres = request.data.get("genres", [])
    if not isinstance(genres, list):
        return Response({"detail": "genres must be an array"}, status=status.HTTP_400_BAD_REQUEST)

    UserPreference.objects.filter(user=request.user).delete()
    created = []
    for genre in dict.fromkeys(str(g).strip() for g in genres if str(g).strip()):
        UserPreference.objects.create(user=request.user, genre_name=genre)
        created.append(genre)
    return Response({"genres": created}, status=status.HTTP_201_CREATED)


@api_view(["GET"])
@authentication_classes([ExistingUserBasicAuthentication])
@permission_classes([IsAuthenticated])
def recommendations(request):
    watched = {
        title.lower()
        for title in Anime.objects.filter(user=request.user).values_list("title", flat=True)
        if title
    }
    genres = {
        genre.lower()
        for genre in UserPreference.objects.filter(user=request.user).values_list("genre_name", flat=True)
        if genre
    }

    candidates = []
    for item in AnimeCatalog.objects.all()[:100]:
        if item.title.lower() in watched:
            continue
        item_genres = {g.strip().lower() for g in (item.genre or "").split(",") if g.strip()}
        match = len(item_genres.intersection(genres))
        candidates.append({
            "anime_id": item.catalog_id,
            "title": item.title,
            "genre": item.genre or "Unknown Genre",
            "total_episodes": item.total_episodes or 0,
            "description": item.description or "",
            "poster_hint": item.poster_hint or item.genre or "Anime",
            "preference_match": match,
        })

    candidates.sort(key=lambda item: item["preference_match"], reverse=True)
    return Response({"results": candidates[:6]})
