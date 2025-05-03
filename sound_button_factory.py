from SoundButton import SoundButton

class SoundButtonFactory:
    @staticmethod
    def create(sound_name):
        return SoundButton(label=sound_name, sound_name=sound_name)
