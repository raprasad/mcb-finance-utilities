from django.contrib.auth.models import User, Group

def get_username(request):
    if request.user and request.user.username:
        return {'username':request.user.username }

    return {}

def is_user_in_group(request, group_name):
    if not (request and request.user):
        return False

    if group_name is None:
        return False

    try:
        group = Group.objects.get(name=group_name)
    except Group.DoesNotExist:
        return False

    for user in group.user_set.get_query_set():
        if request.user == user:
            return True
    return True