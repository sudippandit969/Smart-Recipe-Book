from django.db import models
from django.contrib.auth.models import User

class Receipe(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    receipe_name=models.CharField(max_length=100)
    receipe_description=models.TextField()
    receipe_image=models.ImageField(upload_to="receipe")
    ingredients = models.TextField(blank=True, null=True)
    prep_time = models.IntegerField(default=0, help_text="Preparation time in minutes")
    category = models.CharField(max_length=50, blank=True, null=True)
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    receipe = models.ForeignKey(Receipe, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'receipe')

class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Receipe, on_delete=models.SET_NULL, null=True, blank=True)
    rating = models.IntegerField(default=5)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)