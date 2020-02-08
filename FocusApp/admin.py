from django.contrib import admin

# Register your models here.
from .models import Profile,Project,ProjectUser,Rolls

# Register your models here.
admin.site.register(Profile)

admin.site.register(Project)
admin.site.register(ProjectUser)

admin.site.register(Rolls)
