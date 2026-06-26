from django.http import HttpResponse
from nilpoint.views import NilpointGameBasic
from .models import Module


class CypherpunkGameView(NilpointGameBasic):
    handlers = {"test": "test_view", "deck": "deck_view", "module": "module_view"}

    # landing_partial = "cypherpunk/landing.jinja2#landing"

    def test_view(self, request, *args, **kwargs):
        return HttpResponse("This worked", content_type="text/plain")

    def deck_view(self, request, *args, **kwargs):
        template = "cypherpunk/deck/deck_base.jinja2"
        try:
            pc = self.player_character
            deck = pc.deck
            print(type(pc))
        except Exception as e:
            return HttpResponse(f"Error: {e}")
        return self.nilpoint_render(request, template, {"deck": deck})

    def module_view(self, request, *args, **kwargs):
        module_id = request.GET.get("id", -1)
        module = Module.objects.get_subclass(id=module_id)
        return self.nilpoint_render(request, module.template, {"module": module})
