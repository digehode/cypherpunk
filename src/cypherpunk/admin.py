from django.contrib import admin

from .models import CypherpunkGame, CypherpunkPC, Deck, Module


@admin.register(CypherpunkGame)
class CypherpunkGameAdmin(admin.ModelAdmin):
    model = CypherpunkGame
    prepopulated_fields = {"nilpoint_slug": ("instance_name",)}


@admin.register(CypherpunkPC)
class CypherpunkPCAdmin(admin.ModelAdmin):
    model = CypherpunkPC
    list_display = ["handle", "player", "game"]


@admin.register(Deck)
class DeckAdmin(admin.ModelAdmin):
    model = Deck
    list_display = ["id", "player_character"]


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    model = Module
