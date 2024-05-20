from plyer import notification


def show_notification(title, message):
    notification.notify(
        title=title,
        message=message,
        app_name="Your Application Name",
        timeout=10,  # duration in seconds
    )


# Example usage:
show_notification("Test Notification", "This is a test message.")
