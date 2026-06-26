from .models import Module


class HelpModule(Module):
    """The one module every deck starts with. It has nothing other than some help text to inform the player of what this is."""

    module_type = "Help Module"
    template = "cypherpunk/deck/help_module.jinja2"
    background_image = "cypherpunk/modules/help.png"
