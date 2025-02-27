import os
import json
import joblib

from django.shortcuts import render
from django.http import JsonResponse
from django.shortcuts import render, redirect
from .forms import MoodForm, JournalEntryForm, LoginForm, SignupForm, Activity, ActivityForm
from .models import Mood, JournalEntry, MoodEntry, Activity
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone



# Load the trained model
model = joblib.load(r"D:\projo 1\mental_health\wellness_app\mental_health_model.pkl")

# ✅ Get the current directory of views.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ✅ Correct model path using BASE_DIR
MODEL_PATH = os.path.join(BASE_DIR, "mental_health_model.pkl")

# ✅ Check if the file exists before loading
if os.path.exists(MODEL_PATH):
    print(f"✅ Model found at {MODEL_PATH}, loading...")
    model = joblib.load(MODEL_PATH)
    print("✅ Model loaded successfully!")
else:
    print(f"❌ Model file NOT found at: {MODEL_PATH}")
    model = None  # Avoid crashing if the model is missing

def home(request):
    return render(request, 'home.html')


def activities(request):
    if request.method == 'POST':
        form = ActivityForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('activities')  # Redirect to the same page after submission
        else:
            print(form.errors)  # Log errors for debugging
    else:
        form = ActivityForm()

    activities = Activity.objects.all()
    return render(request, 'activities.html', {'form': form, 'activities': activities})


@login_required
def mood_tracker(request):
    if request.method == 'POST':
        form = MoodForm(request.POST)
        if form.is_valid():
            mood = form.save(commit=False)
            mood.user = request.user
            mood.save()
            return redirect('home')
    else:
        form = MoodForm()
    moods = Mood.objects.filter(user=request.user)
    return render(request, 'mood_tracker.html', {'form': form, 'moods': moods})


@login_required
def journal(request):
    if request.method == 'GET':
        entries = JournalEntry.objects.filter(user=request.user).order_by('-date')
        return render(request, 'journal.html', {'entries': entries})



def signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/login/')  # Redirect after successful signup
    else:
        form = SignupForm()  # Initialize an empty form for GET requests

    return render(request, 'signup.html', {'form': form})


def logout_view(request):
    return render(request, 'logout.html')


import logging

logger = logging.getLogger(__name__)



@login_required
def save_journal(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            date = data.get('date')
            content = data.get('content')

            if not date or not content:
                return JsonResponse({'error': 'Both date and content are required.'}, status=400)

            JournalEntry.objects.create(user=request.user, date=date, content=content)
            return JsonResponse({'message': 'Journal saved successfully!'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid method'}, status=405)


def save_mood(request):
    if request.method == 'POST':
        mood_type = request.POST.get('mood')  # Get the mood type
        description = request.POST.get('notes', '')  # Get optional notes
        user = request.user  # The logged-in user

        if mood_type:
            # Create and save the new mood entry
            mood = Mood(user=user, mood_type=mood_type, description=description)
            mood.save()

            # Return a success message or the saved data
            return JsonResponse({'success': True, 'message': 'Mood saved successfully!'})

        return JsonResponse({'success': False, 'message': 'Mood type is required'})

    return JsonResponse({'success': False, 'message': 'Invalid request'})



@login_required
def get_journal_entries(request):
    try:
        entries = JournalEntry.objects.filter(user=request.user).values('date', 'content')
        return JsonResponse(list(entries), safe=False)
    except Exception as e:
        logger.error(f"Error fetching journal entries: {e}")
        return JsonResponse({'error': str(e)}, status=500)

def mood_tracker(request):
    if request.method == 'POST':
        form = MoodForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('mood_tracker')  # Redirect to the same page after saving
    else:
        form = MoodForm()
    
    # Fetch mood history from the database
    mood_entries = MoodEntry.objects.all().order_by('-date')  # Order by most recent

    return render(request, 'mood_tracker.html', {
        'form': form,
        'mood_entries': mood_entries,
    })
def save_mood_entry(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            mood = data.get('mood')
            notes = data.get('notes')
            
            # Save to the database
            MoodEntry.objects.create(mood=mood, notes=notes)
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)

def add_activity(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            activity_text = data.get('activity')
            duration = data.get('duration')

            # Save to database
            activity = Activity.objects.create(activity=activity_text, duration=duration)
            return JsonResponse({
                'success': True,
                'activity': {
                    'id': activity.id,
                    'activity': activity.activity,
                    'duration': activity.duration,
                }
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)

@csrf_exempt
@require_http_methods(["POST"])
def toggle_activity_completed(request, activity_id):
    try:
        data = json.loads(request.body)
        activity = Activity.objects.get(id=activity_id)
        activity.completed = data.get('completed', False)
        activity.save()
        return JsonResponse({'status': 'success'})
    except Activity.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Activity not found'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)

def activity_list(request):
    activities = Activity.objects.all()
    return render(request, 'activity_tracker.html', {'activities': activities})


def activities_view(request):
    if request.method == 'POST':
        form = ActivityForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('activities')
    else:
        form = ActivityForm()
    
    # Get today's activities
    today = timezone.now().date()
    activities = Activity.objects.filter(
        created_at__date=today
    ).order_by('-created_at')
    
    return render(request, 'activities.html', {
        'form': form, 
        'activities': activities
    })


def chatbot_response(request):
    from .models import YourModel


def chatbot_page(request):
    return render(request, "chatbot.html")


# Load the model safely
try:
    model = joblib.load(MODEL_PATH)
    print(f"Model loaded from {MODEL_PATH}")
except FileNotFoundError:
    model = None
    print(f"Error: Model file not found at {MODEL_PATH}")


@csrf_exempt  # Disable CSRF for testing, but secure it later

def chatbot_view(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_message = data.get("message", "")

            if not user_message:
                return JsonResponse({"error": "Empty message"}, status=400)

            # Sample response logic
            bot_response = f"You said: {user_message}"
            return JsonResponse({"response": bot_response})
        
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
    
    return JsonResponse({"error": "Invalid request"}, status=400)


@csrf_exempt  # Allow requests without CSRF token
def chatbot_response(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_message = data.get("message", "")

            # Sample chatbot response (Replace with actual model logic)
            bot_response = f"You said: {user_message}"

            return JsonResponse({"response": bot_response})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request"}, status=400)