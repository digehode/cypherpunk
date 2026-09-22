from django.apps import apps
from django.db import models
from model_utils.managers import InheritanceManager
from nilpoint.decorators import release_step
from nilpoint.models import Exit, Game, Item, Location, PlayerCharacter, LocationItem


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
        """Create a mystery device item with push_button and turn_off interactions."""
        device = Item(
            asset_id="MYSTERY_DEVICE",
            name="Mystery Device",
            description="A mysterious device with a button labelled 'push me'",
            game=self,
            graphic="",
        )
        device.save()
        # Add interaction hooks
        device.hooks.put("show", {"push_button": "show_push_button_device"})
        device.hooks.put(
            "handle",
            {
                "push_button": "handle_push_button_device",
                "turn_off": "handle_turn_off_device",
            },
        )
        device.hooks.put(
            "can",
            {
                "push_button": "can_push_button_device",
                "turn_off": "can_turn_off_device",
            },
        )

    # Interaction hook methods for mystery device
    def can_push_button_device(self, instance):
        """Can only push button when item is in inventory (InventoryItem)."""
        return instance.__class__.__name__ == "InventoryItem"

    def can_turn_off_device(self, instance):
        """Can only turn off when item is in inventory AND has been pushed."""
        return (
            instance.__class__.__name__ == "InventoryItem"
            and instance.item_state.get("pushed", False)
        )

    def show_push_button_device(self, instance):
        """Return template partial showing the device state."""
        return "cypherpunk/interact/mystery_device.jinja2#push_button"

    def handle_push_button_device(self, instance, request):
        """Mark the device as pushed in its state."""
        instance.item_state.put("pushed", True)

    def handle_turn_off_device(self, instance, request):
        """Turn off the device (reset pushed state)."""
        instance.item_state.put("pushed", False)

    def get_item_hooks(self, item):
        """Return interaction hooks for items in this game."""
        if item.asset_id == "MYSTERY_DEVICE":
            return {
                "show": {"push_button": "show_push_button_device"},
                "handle": {
                    "push_button": "handle_push_button_device",
                    "turn_off": "handle_turn_off_device",
                },
                "can": {
                    "push_button": "can_push_button_device",
                    "turn_off": "can_turn_off_device",
                },
            }
        return {"show": {}, "handle": {}, "can": {}}


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
        """Create a LocationItem for the mystery device at the alley."""
        device = self.game.get_asset("MYSTERY_DEVICE")
        location = self.game.get_asset("ALLEY")
        device_location = LocationItem(location=location, pc=self, item=device)
        device_location.save()


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
