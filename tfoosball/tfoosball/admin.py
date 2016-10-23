from django.contrib import admin
from .models import Player, Match, ExpHistory


class ExpHistoryAdmin(admin.ModelAdmin):
    list_display = ('username', 'date', 'exp',)
    
    def username(self, obj):
        return obj.player.username

admin.site.register(Player)
admin.site.register(Match)
admin.site.register(ExpHistory, ExpHistoryAdmin)
