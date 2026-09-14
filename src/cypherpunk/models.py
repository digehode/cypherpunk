from django.db import models
from nilpoint.models import Game, PlayerCharacter, Location, Exit
from model_utils.managers import InheritanceManager
from django.apps import apps


class CypherpunkGame(Game):
    name = "Cypherpunk: Crouching Cypher, Hidden Punk"
    description = "Cypherpunk is a game of encryption and decryption. Enter a world of stuff, where things happen and people do things."

    def initialise_game_instance(self):
        # Locations
        alley_1 = Location(
            name="An alley off a busy street",
            description="All around is the detritus of a busy city. Wrappers, junk and organic smells.  Something about the signs is off. It might be in a language you don't understand, but it looks more like gibberish.",
            game=self,
            graphic="cypherpunk/locations/01_alley/alley_front.png",
            initial=True,
        )
        alley_2 = Location(
            name="End of an alley",
            description="The same alley, but more so",
            game=self,
            graphic="cypherpunk/locations/01_alley/alley_back.png",
            initial=False,
        )
        alley_1.save()
        alley_2.save()
        e1, e2 = Exit.create_two_way_exit(
            alley_1, "Deeper into the alley", alley_2, "Back up the alley"
        )


class CypherpunkPC(PlayerCharacter):
    def save(self, *args, **kwargs):
        # Check if it's a new instance (no ID yet)
        is_new = self.pk is None

        # Save the player character first so it gets a database ID
        super().save(*args, **kwargs)

        # Now that the player character is saved, create their deck
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

    def __str__(self):
        return f"Deck ({self.id}) for PC {self.player_character.handle}"


class Module(models.Model):
    """Superclass for specific modules"""

    objects = InheritanceManager()
    background_image = "cypherpunk/modules/generic.png"
    template = "cypherpunk/deck/generic_module.jinja2"
    module_type = "generic"
    deck = models.ForeignKey(
        Deck, null=False, on_delete=models.CASCADE, related_name="modules"
    )

    def __str__(self):
        return f"{self.module_type} module ({self.id}) for PC {self.deck.player_character.handle}"
