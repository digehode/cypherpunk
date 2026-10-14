from django.apps import apps
from django.db import models
from model_utils.managers import InheritanceManager
from nilpoint.decorators import release_step
from nilpoint.models import Exit, Game, Item, Location, PlayerCharacter, LocationItem

from .interactions import MysteryDevice, Scanner


class CypherpunkGame(Game):
    name = "Cypherpunk: Crouching Cypher, Hidden Punk"
    description = "Cypherpunk is a game of encryption and decryption. Enter a world of stuff, where things happen and people do things."

    def initialise_game_instance(self):
        pass

    @release_step(1)
    def initial_locations(self):
        # Locations
        alley_1 = Location(
            asset_id="ALLEY",
            name="An alley off a busy street",
            description="All around is the detritus of a busy city. Wrappers, junk and organic smells.  Something about the signs is off. It might be in a language you don't understand, but it looks more like gibberish.",
            game=self,
            graphic="cypherpunk/locations/01_alley/alley_front.png",
            initial=True,
        )
        alley_2 = Location(
            asset_id="ALLEY_END",
            name="End of an alley",
            description="The same alley, but more so",
            game=self,
            graphic="cypherpunk/locations/01_alley/alley_back.png",
            initial=False,
        )
        alley_1.save()
        alley_2.save()
        e1, e2 = Exit.create_two_way_exit(
            alley_1,
            "Deeper into the alley",
            alley_2,
            "Back up the alley",
            asset_id_prefix="ALLEY_EXIT",
        )

    @release_step(2)
    def adding_random_item(self):
        wotsit = Item(
            asset_id="WOTSIT",
            name="A Wotsit",
            description="It's a typical wotsit. A little worn but functional",
            game=self,
            graphic="",
        )
        wotsit.save()

    @release_step(3)
    def test_rel(self):
        thing = self.get_asset("ALLEY_EXIT_B")
        thing.save()

    @release_step(4)
    def test_rel2(self):
        self.default_item_graphic = "nilpoint/ui_elements/item_tmp.png"
        self.save()

    @release_step(5)
    def add_css_etc(self):
        self.css = "cypherpunk/css/cypherpunk.css"
        self.default_location_graphic = "cypherpunk/locations/00_none/simple.png"
        self.save()

    @release_step(6)
    def add_item_graphic(self):
        wotsit = self.get_asset("WOTSIT", Item)
        wotsit.graphic = "nilpoint/ui_elements/dummy_item.png"
        wotsit.save()

    @release_step(7)
    def add_mystery_device(self):
        """Create a mystery device, interactive via the MysteryDevice class.

        All the release step does is name the class that implements the
        behaviour.  The device's two actions, their labels, when they are
        available and what they do all live in `cypherpunk.interactions`.
        """
        Item.objects.create(
            asset_id="MYSTERY_DEVICE",
            name="Mystery Device",
            description="A mysterious device with a button labelled 'push me'",
            game=self,
            graphic="",
            interaction=MysteryDevice.dotted_path(),
        )

    @release_step(8)
    def add_scanner(self):
        """Create a scanner, interactive via the Scanner class.

        The button and display live in the scanner's interaction class; all
        the release step names it and points `interaction_options` at the
        location that has the signal, which the `ScanSignal` action reads.
        """
        Item.objects.create(
            asset_id="SCANNER",
            name="Scanner",
            description="A handheld scanner with a small screen and a single button.",
            game=self,
            graphic="",
            interaction=Scanner.dotted_path(),
            interaction_options={"signal_location": "ALLEY_END"},
        )


    @release_step(9)
    def add_arcade_demo(self):
        """Add a room from the arcade, including the scrap of paper.
        """

        if self.get_asset("SCRAP_A", Item) is None:
            Item.objects.create(
                asset_id="SCRAP_A",
                name="Scrap of Paper",
                description="A scrap of paper with the text \"Tol, S pyexn kx yvn cdybkqo byyw sx dro kvvoi. Xydrsxq yp kxi eco sx sd, led sd vyyuc klkxnyxon. Wsqrd lo k qyyn zvkmo dy dy vso vyg. Dro zkccgybn pyb dro nyyb sc CGYBNPSCR\" written on it",
                game=self,
                graphic="cypherpunk/items/scrap_of_paper_a.png",
            )
        arcade_se=self.get_asset("ARCADE_SE", Location)
        if arcade_se is None:
            arcade_se = Location.objects.create(
                asset_id="ARCADE_SE",
                name="Arcade Corner (SE)",
                description="This corner of the arcade is even quieter than the rest. Most of the arcade machines are out of order.",
                game=self,
                graphic="cypherpunk/locations/02_arcade/arcade_se.png",
                initial=False,
            )
        
        alley=self.get_asset("ALLEY_END", Location)
        print(alley)
        print(arcade_se)
        e1, e2 = Exit.create_two_way_exit(
            alley,
            "Back door to an arcade",
            arcade_se,
            "out into the ally",
            asset_id_prefix="ALLEY_ARCADE_EXIT",
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

    @release_step(1)
    def dummy_update(self):
        print("Doing a dummy update")

    @release_step(2)
    def adding_random_item(self):
        wotsit = self.game.get_asset("WOTSIT")
        location = self.game.get_asset("ALLEY")
        wotsit_location = LocationItem(location=location, pc=self, item=wotsit)
        wotsit_location.save()

    @release_step(6)
    def adding_data_to_wotsits(self):
        wotsit = self.game.get_asset("WOTSIT")
        from itertools import chain

        combined_items = chain(
            wotsit.inventories.for_character(self).all(),
            wotsit.locations.for_character(self).all(),
        )
        for i in combined_items:
            data = i.item_state
            data.put("weight", 100)

    @release_step(7)
    def add_mystery_device_location_item(self):
        """Put the mystery device in the alley for this player's game."""
        device = self.game.get_asset("MYSTERY_DEVICE")
        location = self.game.get_asset("ALLEY")
        LocationItem(location=location, pc=self, item=device).save()

    @release_step(8)
    def add_scanner_location_item(self):
        """Put the scanner in the alley for this player's game."""
        scanner = self.game.get_asset("SCANNER")
        location = self.game.get_asset("ALLEY")
        LocationItem(location=location, pc=self, item=scanner).save()


    @release_step(9)
    def add_scrap_of_paper(self):
        paper=self.game.get_asset("SCRAP_A", Item)
        arcade_se=self.game.get_asset("ARCADE_SE", Location)
        LocationItem(location=arcade_se, pc=self, item=paper).save()
        
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
