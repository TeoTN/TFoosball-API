from rest_framework import permissions

from tfoosball.models import Member


class AccessOwnTeamOnly(permissions.BasePermission):
    message = 'You cannot access team you don\'t belong to.'

    def has_permission(self, request, view):
        accessed_team = view.kwargs.get('pk', None)
        if not accessed_team:
            return True
        return request.user.member_set.filter(team__id=accessed_team).exists()

    def has_object_permission(self, request, view, obj):
        accessed_team = view.kwargs.get('pk', None)
        if not accessed_team or request.user.is_staff:
            return True
        return request.user.member_set.filter(team__id=accessed_team).exists()


class MemberPermissions(permissions.BasePermission):
    message = 'You are not allowed to modify this member.'

    def allow_accepting(self, request, view):
        if request.method not in ['PATCH', 'DELETE']:
            return False
        member_id = view.kwargs.get('pk', None)
        member = Member.objects.filter(pk=member_id).first()
        is_self = request.user.id == member.player.id if member else False
        is_accepting = list(request.data.keys()) in [['is_accepted'], []]
        if is_self or not is_accepting:
            return False
        request_teams = request.user.member_set.all().values_list('team__name', flat=True)
        is_correct_team = view.get_object().team.name in request_teams
        return is_correct_team

    def has_permission(self, request, view):
        if request.method == 'GET':
            return True
        team = view.kwargs.get('parent_lookup_team', None)
        member_id = view.kwargs.get('pk', None)
        is_admin = request.user.member_set.filter(team__id=team, is_team_admin=True).count() > 0
        is_owner = request.user.member_set.filter(team__id=team, id=member_id).count() > 0
        return is_admin or is_owner or self.allow_accepting(request, view)


class IsMatchOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        accessed_team = view.kwargs.get('team', None)
        if not accessed_team:
            return True
        return request.user.member_set.filter(team__id=accessed_team).exists()

    def has_object_permission(self, request, view, obj):
        owners = [u.pk for u in obj.users]
        return request.user.member_set.filter(pk__in=owners).count() > 0


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        accessed_team = view.kwargs.get('team', None)
        if not accessed_team:
            return True
        return request.user.member_set.filter(team__id=accessed_team).is_team_admin
