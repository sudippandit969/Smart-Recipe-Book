import os
import django
import random
import string
import urllib.request
from django.core.files.base import ContentFile

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jangoproject.settings')
django.setup()

from django.contrib.auth.models import User
from vege.models import Receipe

# Download a few placeholder images from Unsplash
image_urls = [
    "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1482049016688-2d3e1b311543?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1473093295043-cdd812d0e601?auto=format&fit=crop&w=800&q=80"
]

print("Downloading placeholder images...")
saved_images = []
for i, url in enumerate(image_urls):
    try:
        response = urllib.request.urlopen(url)
        saved_images.append((f"food_placeholder_{i}.jpg", response.read()))
    except Exception as e:
        print(f"Failed to download {url}: {e}")

print(f"Downloaded {len(saved_images)} images.")

categories = ["Breakfast", "Lunch", "Dinner", "Dessert", "Snack"]
adjectives = ["Spicy", "Creamy", "Crispy", "Savory", "Sweet", "Zesty", "Classic", "Homestyle", "Premium", "Quick"]
foods = ["Chicken", "Pasta", "Salad", "Beef", "Tofu", "Curry", "Sandwich", "Bowl", "Soup", "Pizza"]

print("Generating 20 users and 200 recipes in the cloud database...")

for i in range(20):
    username = f"chef_{''.join(random.choices(string.ascii_lowercase, k=6))}"
    
    # Check if user already exists just in case
    if not User.objects.filter(username=username).exists():
        user = User.objects.create_user(username=username, email=f"{username}@example.com", password="password123")
        
        for j in range(10):
            recipe_name = f"{random.choice(adjectives)} {random.choice(foods)} {random.randint(100, 999)}"
            
            recipe = Receipe(
                user=user,
                receipe_name=recipe_name,
                receipe_description=f"This {recipe_name} is absolutely delicious and perfect for any occasion! It is easy to make and packed with incredible flavor. Don't forget to use fresh ingredients for the best results.",
                ingredients="2 cups Main Ingredient\n1 tbsp Olive Oil\n1 tsp Salt\n1/2 tsp Black Pepper\n1 tsp Garlic Powder\nFresh herbs for garnish",
                prep_time=random.randint(15, 90),
                category=random.choice(categories),
                is_public=True
            )
            
            if saved_images:
                img_name, img_data = random.choice(saved_images)
                recipe.receipe_image.save(img_name, ContentFile(img_data), save=False)
                
            recipe.save()
            
        print(f"[{i+1}/20] Created user {username} with 10 recipes.")

print("Successfully seeded the database!")
