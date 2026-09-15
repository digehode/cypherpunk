from django.apps import apps
from django.db import models
from model_utils.managers import InheritanceManager
from nilpoint.decorators import release_step
from nilpoint.models import Exit, Game, Item, Location, PlayerCharacter, LocationItem


class CypherpunkGame(Game):
    name = "Cypherpunk: Crouching Cypher, Hidden Punk"
    description = "Cypherpunk is a game of encryption and decryption. Enter a world of stuff, where things happen and people do things."

    _latest_release = 2

    def initialise_game_instance(self):
        pass

    def latest_release(self):
        return self._latest_release

    @release_step(1)
    def initial_locations(self):
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
        return True

    @release_step(2)
    def adding_random_item(self):
        wotsit = Item(
            name="A Wotsit",
            description="It's a typical wotsit. A little worn but functional",
            game=self,
            graphic="",
        )
        wotsit.save()
        return True


class CypherpunkPC(PlayerCharacter):
    def save(self, *args, **kwargs):
        # Check if it's a new instance (no ID yet)
        is_new = self.pk is None

        # Save the player character first so it gets a database ID
        super().save(*args, **kwargs)

        # Now that the player character is saved, create their deck
        if is_new:
            Deck.objects.create(player_character=self)

    @release_step(1)
    def dummy_update(self):
        print("Doing a dummy update")
        return True

    @release_step(2)
    def adding_random_item(self):
        wotsit = Item.objects.get(game=self.game, name="A Wotsit")
        for i in Location.objects.filter(game=self.game):
            print(i)
        location = Location.objects.get(id=1)
        wotsit_location = LocationItem(location=location, pc=self, item=wotsit)
        wotsit_location.save()
        return True


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
