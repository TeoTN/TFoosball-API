from rest_framework import permissions


class AccessOwnTeamOnly(permissions.BasePermission):
    message = 'You cannot access team you don\'t belong to.'

    def has_permission(self, request, view):
        accessed_team = view.kwargs['team']
        if not accessed_team:
            return True
        return request.user.member_set.filter(team__domain=accessed_team).count() > 0
