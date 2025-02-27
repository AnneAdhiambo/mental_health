from django.contrib import admin
from .models import JournalEntry, Mood, Activity

# Register each model separately
admin.site.register(JournalEntry)
admin.site.register(Mood)
admin.site.register(Activity)
