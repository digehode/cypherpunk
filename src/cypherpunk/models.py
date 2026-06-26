from django.db import models
from nilpoint.models import Game, PlayerCharacter
from model_utils.managers import InheritanceManager
from django.apps import apps


class CypherpunkGame(Game):
    name = "Cypherpunk: Crouching Cypher, Hidden Punk"
    description = "Cypherpunk is a game of encryption and decryption. Enter a world of stuff, where things happen and people do things."


class CypherpunkPC(PlayerCharacter):
    def save(self, *args, **kwargs):
        # Check if it's a new instance (no ID yet)
        is_new = self.pk is None

        # Save A first so it gets a database ID
        super().save(*args, **kwargs)

        # Now that A is saved, create B
        if is_new:
            Deck.objects.create(player_character=self)


class Deck(models.Model):
    """Represents the comms deck of a player character


    TODO: individual deck settings in here? Volume, for eg?
    """

    player_character = models.OneToOneField(
        CypherpunkPC, null=False, on_delete=models.CASCADE, related_name="deck"
    )

    def save(self, *args, **kwargs):
        # Check if it's a new instance (no ID yet)
        is_new = self.pk is None

        # Save A first so it gets a database ID
        super().save(*args, **kwargs)

        # Now that A is saved, create B
        if is_new:
            HelpModuleClass = apps.get_model("cypherpunk", "HelpModule")
            HelpModuleClass.objects.create(deck=self)


class Module(models.Model):
    """Superclass for specific modules"""

    objects = InheritanceManager()
    background_image = "cypherpunk/modules/generic.png"
    template = "cypherpunk/deck/generic_module.jinja2"
    module_type = "generic"
    deck = models.ForeignKey(
        Deck, null=False, on_delete=models.CASCADE, related_name="modules"
    )
