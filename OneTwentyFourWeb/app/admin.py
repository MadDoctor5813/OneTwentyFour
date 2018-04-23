from django.contrib import admin
from app.models import Riding, PartyResult

class PartyResultInline(admin.TabularInline):
    model = Riding.results.through 

class PartyResultAdmin(admin.ModelAdmin):
    pass

admin.site.register(PartyResult, PartyResultAdmin)

class RidingAdmin(admin.ModelAdmin):
    inlines = [PartyResultInline,]
    exclude = ('results',) #exclude the field you put the inline on so you dont have double fields

admin.site.register(Riding, RidingAdmin)
