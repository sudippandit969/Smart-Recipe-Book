from django.shortcuts import render
from vege.models import Receipe, Feedback, Favorite
from django.db.models import Count

def home(request):
    # Get top recipes (public only), annotated with favorite counts
    top_recipes = Receipe.objects.filter(is_public=True).annotate(fav_count=Count('favorite')).order_by('-fav_count')[:3]
    
    # Get recent feedback
    recent_feedback = Feedback.objects.select_related('user', 'recipe').order_by('-created_at')[:4]
    
    return render(request, "index.html", {
        "top_recipes": top_recipes,
        "recent_feedback": recent_feedback
    })

def contact(request):
    return render(request, "html/contact.html")

def about(request):
    return render(request, "html/about.html")
