from io import BytesIO

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.files.base import ContentFile
from django.db import models
from PIL import Image, ImageDraw, ImageFont

from team_finder.constants import (AVATAR_BACKGROUND_COLOR, AVATAR_FONT_SIZE,
                                   AVATAR_SIZE, AVATAR_TEXT_ANCHOR,
                                   AVATAR_TEXT_COLOR, AVATAR_VERTICAL_OFFSET,
                                   USER_ABOUT_MAX_LENGTH, USER_NAME_MAX_LENGTH,
                                   USER_PHONE_MAX_LENGTH,
                                   USER_SURNAME_MAX_LENGTH)

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)

    name = models.CharField(max_length=USER_NAME_MAX_LENGTH)
    surname = models.CharField(max_length=USER_SURNAME_MAX_LENGTH)

    avatar = models.ImageField(upload_to="avatars/", blank=True)

    phone = models.CharField(
        max_length=USER_PHONE_MAX_LENGTH,
        unique=True,
    )

    github_url = models.URLField(blank=True)
    about = models.TextField(max_length=USER_ABOUT_MAX_LENGTH, blank=True)

    favorites = models.ManyToManyField(
        "projects.Project",
        blank=True,
        related_name="interested_users",
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "surname"]

    objects = UserManager()

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.name} {self.surname}"

    def save(self, *args, **kwargs):
        if not self.avatar:
            self.avatar = self.generate_avatar()
        super().save(*args, **kwargs)

    def generate_avatar(self):
        image = Image.new(
            "RGB",
            (AVATAR_SIZE, AVATAR_SIZE),
            AVATAR_BACKGROUND_COLOR,
        )

        draw = ImageDraw.Draw(image)

        letter = self.name[0].upper() if self.name else "U"

        try:
            font = ImageFont.truetype("arial.ttf", AVATAR_FONT_SIZE)
        except Exception:
            font = ImageFont.load_default()
            font.size = AVATAR_FONT_SIZE

        bbox = draw.textbbox(AVATAR_TEXT_ANCHOR, letter, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        position = (
            (AVATAR_SIZE - text_width) / 2,
            (AVATAR_SIZE - text_height) / 2 - AVATAR_VERTICAL_OFFSET,
        )

        draw.text(position, letter, fill=AVATAR_TEXT_COLOR, font=font)

        buffer = BytesIO()
        image.save(buffer, format="PNG")

        filename = f"avatar_{self.email.replace('@', '_')}.png"

        return ContentFile(buffer.getvalue(), name=filename)
