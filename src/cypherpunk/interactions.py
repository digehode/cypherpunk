"""Interactions for the Cypherpunk test game.

This is the worked example of how a game gives an item its behaviour.  Each
class here is a plain Python class, not a Django model, and is named by an
`Item`'s `interaction` field in a release step.  Because the behaviour lives
in its own class rather than on the `Game`, several items can share it, and
it can be read, tested and changed on its own.

The split to see here: an `InteractiveItem` declares what a thing is and
judges when its actions are available (`can`); each `Action` is where the
effect of one named thing lives (`handle`).
"""

from nilpoint.interactions import Action, InteractiveItem, SetState


class MysteryDevice(InteractiveItem):
    """A device with a button that has to be pushed before it can be switched off.

    The button only works once the device is in the player's inventory, and
    "turn off" is only offered once the device has been pushed.  Both actions
    are the framework generic `SetState` - one pins `pushed` True, the other
    False - so the class itself is nothing but judgement and the panel.
    """

    partial = "cypherpunk/interact/mystery_device.jinja2#device"

    actions = [
        SetState(
            "push_button",
            label="Push button",
            state_key="pushed",
            value=True,
            message="The device whirs and settles into a steady hum.",
        ),
        SetState(
            "turn_off",
            label="Turn off",
            state_key="pushed",
            value=False,
            message="The device falls silent.",
        ),
    ]

    def can(self, instance, action):
        """Offer "push button" before the device is on, and "turn off" after.

        The device has to be carried: pushing a button through the glass of a
        display case is not a thing.
        """
        if not instance.is_in_inventory:
            return False
        is_pushed = bool(instance.item_state.get("pushed", False))
        return is_pushed == (action.name == "turn_off")

    def get_context(self, instance):
        return {"pushed": bool(instance.item_state.get("pushed", False))}


class ScanSignal(Action):
    """Set the scanner's `signal` state from the player's current location.

    A scan records what it finds on the player's copy of the scanner, so the
    display holds the result of the last scan until it is changed.  The
    location that carries the signal comes from the item's
    `interaction_options` (`signal_location`), so the same action could serve
    another item pointed at a different place; `signal_location` is the class
    default.
    """

    state_key = "signal"
    signal_location = None

    def handle(self, instance, interaction, request):
        target = interaction.options.get("signal_location") or self.signal_location
        here = interaction.pc.current_location
        found = here is not None and here.asset_id == target
        self.set_state(instance, found)


class Scanner(InteractiveItem):
    """A scanner with a button and a display.

    The display reads "---" until the button is pressed, at which point the
    scan writes the result to the scanner's state and the display shows
    "signal found" or "no signal".  The button is only usable while the
    scanner is carried.
    """

    partial = "cypherpunk/interact/scanner.jinja2#device"

    actions = [ScanSignal("scan", label="Press the button")]

    def can(self, instance, action):
        """The button is only clickable once the scanner is in the inventory."""
        return instance.is_in_inventory

    def get_context(self, instance):
        signal = instance.item_state.get("signal")
        if signal is None:
            display = "---"
        elif signal:
            display = "signal found"
        else:
            display = "no signal"
        return {"display": display}
