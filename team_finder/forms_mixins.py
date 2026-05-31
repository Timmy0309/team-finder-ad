from django import forms

from team_finder.constants import GITHUB_DOMAIN


class GithubUrlValidationMixin:
    def clean_github_url(self):
        github_url = self.cleaned_data.get("github_url", "")

        if github_url and GITHUB_DOMAIN not in github_url.lower():
            raise forms.ValidationError("Ссылка должна вести на GitHub")

        return github_url
