from django.contrib import admin
from .models import User, Schedule, Note, AI_Feedback

admin.site.register(User)
admin.site.register(Schedule)
admin.site.register(Note)
admin.site.register(AI_Feedback)
