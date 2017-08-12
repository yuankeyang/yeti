from core.user import User

__description__ = "Create permissions for Inline Analytics"


def migrate():
    for u in User.all():
        u.permissions['inlineanalytics'] = u.permissions['scheduledanalytics']
        u.save()
