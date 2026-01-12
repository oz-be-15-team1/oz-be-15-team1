from allauth.account.forms import SignupForm


class CustomSignupForm(SignupForm):
    def save(self, request):
        user = super().save(request)
        user.name = self.cleaned_data.get("name", "") or user.name
        user.phone = self.cleaned_data.get("phone") or user.phone
        user.save(update_fields=["name", "phone"])
        return user
