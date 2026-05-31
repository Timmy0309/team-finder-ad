import re

from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import PasswordChangeForm

from team_finder.forms_mixins import GithubUrlValidationMixin

from .models import User
from .services import normalize_phone


class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Пароль")

    class Meta:
        model = User
        fields = ["name", "surname", "email", "password"]


class LoginForm(forms.Form):
    email = forms.EmailField(label="Email")
    password = forms.CharField(widget=forms.PasswordInput, label="Пароль")

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")

        if email and password:
            user = authenticate(username=email, password=password)

            if user is None:
                raise forms.ValidationError("Неверный имейл или пароль")

            cleaned_data["user"] = user

        return cleaned_data


class EditProfileForm(GithubUrlValidationMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ["name", "surname", "avatar", "about", "phone", "github_url"]

    def clean_phone(self):
        phone = self.cleaned_data.get("phone", "")

        if not phone:
            return None

        phone = normalize_phone(phone)

        if not re.match(r"^\+7\d{10}$", phone):
            raise forms.ValidationError(
                "Телефон должен быть в формате 8XXXXXXXXXX или +7XXXXXXXXXX"
            )

        users = User.objects.filter(phone=phone)

        if self.instance:
            users = users.exclude(pk=self.instance.pk)

        if users.exists():
            raise forms.ValidationError("Этот номер телефона уже используется")

        return phone


class PasswordChangeUserForm(PasswordChangeForm):
    pass
