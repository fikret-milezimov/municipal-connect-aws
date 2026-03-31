def unread_notifications(request):
    if not request.user.is_authenticated:
        return {"has_unread_notifications": False}

    return {
        "has_unread_notifications": request.user.notifications.filter(
            is_read=False
        ).exists()
    }
