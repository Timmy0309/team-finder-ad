from .models import User


def normalize_phone(phone):
    phone = phone.strip()

    if phone.startswith("8"):
        return "+7" + phone[1:]

    return phone


def get_ordered_users():
    return User.objects.order_by("created_at")
