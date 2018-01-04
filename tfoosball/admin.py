from django.contrib import admin
from .models import Player, Team, Member, ExpHistory, Match, PlayerPlaceholder, WhatsNew


class ExpHistoryAdmin(admin.ModelAdmin):
    list_display = ('username', 'date', 'exp',)

    def username(self, obj):
        return obj.player.username


class TeamAdmin(admin.ModelAdmin):
    list_display = ('name',)


admin.site.register(Player)
admin.site.register(WhatsNew)
admin.site.register(Match)
admin.site.register(Member)
admin.site.register(PlayerPlaceholder)
admin.site.register(Team, TeamAdmin)
admin.site.register(ExpHistory, ExpHistoryAdmin)
