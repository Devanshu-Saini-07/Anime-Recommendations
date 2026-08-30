from django.db import models


class User(models.Model):
    user_id = models.AutoField(primary_key=True, db_column="user_id")
    username = models.CharField(max_length=50)
    email = models.EmailField(max_length=120)
    password_hash = models.CharField(max_length=255, db_column="password_hash")
    preferences_completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "users"

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def __str__(self):
        return self.username


class Anime(models.Model):
    anime_id = models.AutoField(primary_key=True, db_column="anime_id")
    title = models.CharField(max_length=100)
    genre = models.CharField(max_length=50, null=True, blank=True)
    status = models.CharField(max_length=50, null=True, blank=True)
    total_episodes = models.IntegerField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    poster_hint = models.CharField(max_length=100, null=True, blank=True)
    poster_url = models.CharField(max_length=500, null=True, blank=True)
    user = models.ForeignKey(User, db_column="user_id", on_delete=models.DO_NOTHING, related_name="anime")

    class Meta:
        managed = False
        db_table = "anime"
        ordering = ["-anime_id"]


class UserPreference(models.Model):
    preference_id = models.AutoField(primary_key=True, db_column="preference_id")
    user = models.ForeignKey(User, db_column="user_id", on_delete=models.DO_NOTHING, related_name="preferences")
    genre_name = models.CharField(max_length=50)
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "user_preferences"


class AnimeCatalog(models.Model):
    catalog_id = models.AutoField(primary_key=True, db_column="catalog_id")
    title = models.CharField(max_length=100)
    genre = models.CharField(max_length=100, null=True, blank=True)
    total_episodes = models.IntegerField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    poster_hint = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        managed = False
        db_table = "anime_catalog"
        ordering = ["-catalog_id"]
