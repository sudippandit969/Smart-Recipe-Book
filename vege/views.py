from django.shortcuts import render, redirect
from .models import Receipe, Favorite, Feedback
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden, JsonResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.conf import settings
import google.generativeai as genai
import json

# --- Recipe Views ---

@never_cache
@login_required(login_url="/login/")
def receipes(request):
    if request.method == "POST":
        data = request.POST
        receipe_name = data.get('receipe_name')
        receipe_description = data.get('receipe_description')
        receipe_image = request.FILES.get('receipe_image')
        
        ingredients = data.get('ingredients', '')
        prep_time = data.get('prep_time', 0)
        if prep_time == '': prep_time = 0
        category = data.get('category', '')
        is_public = data.get('is_public') == 'on'

        Receipe.objects.create(
            user=request.user,
            receipe_image=receipe_image,
            receipe_name=receipe_name,
            receipe_description=receipe_description,
            ingredients=ingredients,
            prep_time=prep_time,
            category=category,
            is_public=is_public
        )
        return redirect('/receipes/')

    queryset = Receipe.objects.filter(user=request.user).order_by('-created_at')

    if request.GET.get('search'):
        queryset = queryset.filter(receipe_name__icontains=request.GET.get('search'))
    if request.GET.get('category'):
        queryset = queryset.filter(category=request.GET.get('category'))

    context = {'receipes': queryset}
    return render(request, 'receipes.html', context)

@login_required(login_url="/login/")
def delete_receipe(request, id):
    try:
        queryset = Receipe.objects.get(id=id)
        if queryset.user == request.user:
            queryset.delete()
    except Receipe.DoesNotExist:
        pass
    return redirect('/receipes/')

@login_required(login_url="/login/")
def update_receipe(request, id):
    try:
        queryset = Receipe.objects.get(id=id)
    except Receipe.DoesNotExist:
        return redirect('/receipes/')

    if queryset.user != request.user:
        return HttpResponseForbidden("You are not allowed to edit this recipe.")

    if request.method == "POST":
        data = request.POST
        queryset.receipe_name = data.get('receipe_name')
        queryset.receipe_description = data.get('receipe_description')
        queryset.ingredients = data.get('ingredients', '')
        
        prep_time = data.get('prep_time', 0)
        queryset.prep_time = prep_time if prep_time else 0
        
        queryset.category = data.get('category', '')
        queryset.is_public = data.get('is_public') == 'on'

        receipe_image = request.FILES.get('receipe_image')
        if receipe_image:
            queryset.receipe_image = receipe_image

        queryset.save()
        return redirect('/receipes/')

    context = {'receipe': queryset}
    return render(request, 'update_receipes.html', context)

# --- Community & AI Views ---

def community_feed(request):
    queryset = Receipe.objects.filter(is_public=True).order_by('-created_at')
    
    if request.GET.get('search'):
        queryset = queryset.filter(receipe_name__icontains=request.GET.get('search'))
    if request.GET.get('category'):
        queryset = queryset.filter(category=request.GET.get('category'))

    favorites = []
    if request.user.is_authenticated:
        favorites = Favorite.objects.filter(user=request.user).values_list('receipe_id', flat=True)

    context = {
        'receipes': queryset,
        'favorites': favorites
    }
    return render(request, 'community.html', context)

@login_required(login_url="/login/")
def toggle_favorite(request, id):
    try:
        receipe = Receipe.objects.get(id=id)
        fav, created = Favorite.objects.get_or_create(user=request.user, receipe=receipe)
        if not created:
            fav.delete() # Unfavorite if it already exists
    except Receipe.DoesNotExist:
        pass
    
    # Redirect back to where the user came from
    next_url = request.META.get('HTTP_REFERER', '/community/')
    return redirect(next_url)

@login_required(login_url="/login/")
def ai_generate_recipe(request):
    """
    Calls Google Gemini API to generate a recipe based on user input.
    """
    if request.method == "POST":
        prompt = request.POST.get('prompt', '')
        
        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-flash-latest')
            
            system_prompt = f"""
            You are a professional chef. Given the following user input/ingredients: "{prompt}",
            generate a realistic recipe. 
            Return ONLY a raw JSON object (without markdown code blocks, do not include ```json) with the following exact keys:
            - name (string: The name of the dish)
            - description (string: A 2-sentence mouthwatering description)
            - ingredients (string: A bulleted list of ingredients with measurements, separated by newlines)
            - prep_time (integer: Preparation and cooking time in minutes)
            - category (string: e.g. Breakfast, Lunch, Dinner, Dessert)
            """
            
            response = model.generate_content(system_prompt)
            
            # Clean up the response to ensure it's pure JSON
            text = response.text.strip()
            if text.startswith('```json'):
                text = text[7:]
            if text.endswith('```'):
                text = text[:-3]
            text = text.strip()
            
            recipe_data = json.loads(text)
            
            return JsonResponse({
                "name": recipe_data.get("name", "AI Recipe"),
                "description": recipe_data.get("description", ""),
                "ingredients": recipe_data.get("ingredients", ""),
                "prep_time": recipe_data.get("prep_time", 30),
                "category": recipe_data.get("category", "Dinner")
            })
            
        except Exception as e:
            print(f"Gemini API Error: {e}")
            return JsonResponse({"error": "Failed to generate recipe using AI. Please try again."}, status=500)
            
    return JsonResponse({"error": "Invalid request"}, status=400)

@login_required(login_url="/login/")
def smart_suggest_products(request, recipe_id):
    """
    Analyzes a recipe using Gemini and returns recommended products.
    """
    try:
        recipe = Receipe.objects.get(id=recipe_id)
        
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-flash-latest')
        
        prompt = f"""
        Analyze this recipe:
        Name: {recipe.receipe_name}
        Ingredients: {recipe.ingredients}
        Description: {recipe.receipe_description}
        
        Suggest exactly 2 premium spices/masalas and exactly 2 essential kitchen tools required to make this dish.
        Return ONLY a raw JSON array (without markdown code blocks, do not include ```json) of exactly 4 objects.
        Each object must have these keys:
        - name (string: The product name, e.g., "Premium Garam Masala")
        - description (string: 1 sentence why it's needed)
        - price (string: A realistic price, e.g., "$5.99")
        - type (string: either "Spice" or "Tool")
        """
        
        response = model.generate_content(prompt)
        text = response.text.strip()
        if text.startswith('```json'):
            text = text[7:]
        if text.endswith('```'):
            text = text[:-3]
        text = text.strip()
        
        products = json.loads(text)
        return JsonResponse({"products": products})
        
    except Receipe.DoesNotExist:
        return JsonResponse({"error": "Recipe not found"}, status=404)
    except Exception as e:
        print(f"Gemini API Error (Suggest): {e}")
        return JsonResponse({"error": "Failed to load smart suggestions"}, status=500)

# --- Authentication & Misc Views ---

def login_page(request):
    if request.user.is_authenticated:
        return redirect('/receipes/')

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Successfully logged in!")
            return redirect('/receipes/')
        else:
            messages.error(request, "Invalid username or password.")
            return redirect('/login/')

    return render(request, 'login.html')

@never_cache
def logout_page(request):
    if request.user.is_authenticated:
        logout(request)
        request.session.flush()
    response = HttpResponseRedirect('/login/')
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response

def register_page(request):
    if request.user.is_authenticated:
        return redirect('/receipes/')
        
    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email', '')
        password = request.POST.get('password')

        if User.objects.filter(username=username).exists():
            messages.info(request, "Username already exists!")
            return redirect('/register/')

        user = User.objects.create(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email
        )
        user.set_password(password)
        user.save()
        messages.success(request, "Account created successfully! Please login.")
        return redirect('/login/')

    return render(request, 'register.html')

def social(request):
    return render(request, 'html/socialmedia.html')

@login_required(login_url="/login/")
def feedback_page(request):
    if request.method == "POST":
        rating = request.POST.get('rating', 5)
        comment = request.POST.get('comment', '')
        recipe_id = request.POST.get('recipe_id')
        
        recipe = None
        if recipe_id:
            try:
                recipe = Receipe.objects.get(id=recipe_id)
            except Receipe.DoesNotExist:
                pass
                
        Feedback.objects.create(
            user=request.user,
            recipe=recipe,
            rating=int(rating),
            comment=comment
        )
        messages.success(request, "Thank you for your feedback!")
        return redirect('/')
        
    recipes = Receipe.objects.filter(is_public=True)
    return render(request, 'feedback.html', {'recipes': recipes})
        recipe = None
        if recipe_id:
            try:
                recipe = Receipe.objects.get(id=recipe_id)
            except Receipe.DoesNotExist:
                pass
                
        Feedback.objects.create(
            user=request.user,
            recipe=recipe,
            rating=int(rating),
            comment=comment
        )
        messages.success(request, "Thank you for your feedback!")
        return redirect('/')
        
    recipes = Receipe.objects.filter(is_public=True)
    return render(request, 'feedback.html', {'recipes': recipes})
