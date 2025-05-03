from discord.ui import View
from constants import AVAILABLE_SOUNDS
from sound_button_factory import SoundButtonFactory


def create_sound_list_view():
    view = View()
    for sound_name in AVAILABLE_SOUNDS:
        view.add_item(SoundButtonFactory.create(sound_name))
    return view

async def send_sound_list_message(message):
    view = create_sound_list_view()
    await message.channel.send("Click a sound to play:", view=view)

async def send_sound_list_interaction(interaction):
    view = create_sound_list_view()
    await interaction.followup.send("Click a sound to play:", view=view)
