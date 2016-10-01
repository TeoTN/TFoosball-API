from django.views.generic import TemplateView
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from rest_auth.registration.views import SocialLoginView


class GoogleLoginView(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter


class CallbackView(TemplateView):
    template_name = 'callback.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        print(request.GET)
        context['access_token'] = request.GET.get('access_token')
        context['token_type'] = request.GET.get('token_type')
        context['expires_in'] = request.GET.get('expires_in')
        return self.render_to_response(context)
