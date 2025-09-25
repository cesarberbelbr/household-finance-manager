from django.views.generic import TemplateView

class HomePageView(TemplateView):
    """
    A view to render the main home page template.
    """
    template_name = "home.html"