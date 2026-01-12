from allauth.account.adapter import DefaultAccountAdapter


class CustomAccountAdapter(DefaultAccountAdapter):
    def get_phone(self, request, *args, **kwargs):
        if request and hasattr(request, "POST"):
            return request.POST.get("phone")
        return None
