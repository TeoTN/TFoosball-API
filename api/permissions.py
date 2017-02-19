from rest_framework import permissions


class AccessOwnTeamOnly(permissions.BasePermission):
    message = 'You cannot access team you don\'t belong to.'

    def has_permission(self, request, view):
        accessed_team = view.kwargs.get('team', None)
        if not accessed_team:
            return True
        return request.user.member_set.filter(team__domain=accessed_team).count() > 0


class MemberDeletePermission(permissions.BasePermission):
    message = 'You cannot remove this member.'

    def has_permission(self, request, view):
        if request.method == 'GET':
            return True
        team = view.kwargs.get('parent_lookup_team', None)
        member_id = view.kwargs.get('pk', None)
        is_admin = request.user.member_set.filter(team__domain=team, is_team_admin=True).count() > 0
        is_owner = request.user.member_set.filter(team__domain=team, pk=member_id).count() > 0
        return is_admin or is_owner
