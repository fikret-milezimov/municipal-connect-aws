def is_moderator(user):
    return user.groups.filter(name="Moderators").exists()


def is_content_manager(user):
    return user.groups.filter(name="ContentManagers").exists()