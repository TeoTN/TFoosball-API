from django.views.generic import TemplateView
import os


class CallbackView(TemplateView):
    template_name = 'callback.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context['access_token'] = request.GET.get('access_token')
        context['token_type'] = request.GET.get('token_type')
        context['expires_in'] = request.GET.get('expires_in')
        context['FRONTEND_CLIENT'] = os.environ.get('FRONTEND_CLIENT', 'http://localhost:3000/')
        return self.render_to_response(context)
