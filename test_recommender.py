from gemini_recommender import get_recommendations


preferences = [
    "Action",
    "Fantasy",
    "Dark Fantasy"
]

watch_history = [
    "Demon Slayer",
    "Attack on Titan"
]

candidates = [
    {
        "title": "Jujutsu Kaisen",
        "genres": ["Action", "Dark Fantasy"]
    },
    {
        "title": "Solo Leveling",
        "genres": ["Action", "Fantasy"]
    },
    {
        "title": "Death Note",
        "genres": ["Psychological", "Thriller"]
    },
    {
        "title": "One Piece",
        "genres": ["Action", "Adventure", "Fantasy"]
    }
]


recommendations = get_recommendations(
    preferences,
    watch_history,
    candidates
)

print("\nRecommendations:\n")

for anime in recommendations:
    print(anime)