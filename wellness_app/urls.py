from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView
from.forms import LoginForm
from .views import activities_view, chatbot_page, toggle_activity_completed
from .views import chatbot_response
from .views import chatbot_view  # Change to match your function name



urlpatterns = [
    path('', views.home, name='home'),
    path('mood_tracker/', views.mood_tracker, name='mood_tracker'),
    path('journal/', views.journal, name='journal'),
    path('activities/', views.activities, name='activities'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html', authentication_form=LoginForm), name='login'),
    path('signup/',views.signup,name='signup'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('save_journal/', views.save_journal, name='save_journal'),
    path('journal/', views.get_journal_entries, name='get_journal_entries'),
    path('save_mood/', views.save_mood, name='save_mood'),
    path('save-mood-entry/', views.save_mood_entry, name='save_mood_entry'),
    path('add-activity/', views.add_activity, name='add_activity'),
    path('activities/', views.activity_list, name='activity_list'),
    path('activities/toggle-completed/<int:activity_id>/', views.toggle_activity_completed, name='toggle_activity_completed'),
    path("chatbot/", chatbot_response, name="chatbot_response"),
    path("chatbot-page/", chatbot_page, name="chatbot_page"),
    path("api/chatbot/", chatbot_view, name="chatbot"),
    path("api/chatbot/", chatbot_response, name="chatbot_response"),




]