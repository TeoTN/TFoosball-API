from rest_framework import permissions


class AccessOwnTeamOnly(permissions.BasePermission):
    message = 'You cannot access team you don\'t belong to.'

    def has_permission(self, request, view):
        accessed_team = view.kwargs.get('team', None)
        if not accessed_team:
            return True
        return request.user.member_set.filter(team__id=accessed_team).count() > 0


class MemberPermissions(permissions.BasePermission):
    message = 'You are not allowed to modify this member.'

    def allow_accepting(self, request, view):
        if request.method not in ['PATCH', 'DELETE']:
            print('wrong method')
            return False
        member_id = view.kwargs.get('pk', None)
        is_self = request.user.id == member_id
        is_accepting = list(request.data.keys()) in [['is_accepted'], []]
        if is_self or not is_accepting:
            print('self or not is_accepting', is_self, is_accepting, list(request.data.keys()))
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
