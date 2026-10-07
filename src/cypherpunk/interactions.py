"""Interactions for the Cypherpunk test game.

This is the worked example of how a game gives an item its behaviour.  Each
class here is a plain Python class, not a Django model, and is named by an
`Item`'s `interaction` field in a release step.  Because the behaviour lives
in its own class rather than on the `Game`, several items can share it, and
it can be read, tested and changed on its own.
"""

from nilpoint.interactions import Action, InteractiveItem
from nilpoint.views import HtmxTriggerResponse


class MysteryDevice(InteractiveItem):
    """A device with a button that has to be pushed before it can be switched off.

    The button only works once the device is in the player's inventory, and
    "turn off" is only offered once the device has been pushed.  The state of
    the device is per-player, so it lives in the `item_state` of the
    InventoryItem rather than anywhere on the Item.
    """

    partial = "cypherpunk/interact/mystery_device.jinja2#device"

    actions = [
        Action("push_button", label="Push button"),
        Action("turn_off", label="Turn off"),
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

    def handle(self, instance, action, request):
        """Flip the device on or off and tell the player what happened."""
        pushed = action.name == "push_button"
        instance.item_state.put("pushed", pushed)
        if pushed:
            return HtmxTriggerResponse(
                content="The device whirs and settles into a steady hum.",
                content_type="text/plain",
            )
        return HtmxTriggerResponse(
            content="The device falls silent.",
            content_type="text/plain",
        )

    def get_context(self, instance):
        """Add the device's status to the panel context."""
        return {"pushed": bool(instance.item_state.get("pushed", False))}
