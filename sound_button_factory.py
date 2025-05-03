from SoundButton import SoundButton

class SoundButtonFactory:
    @staticmethod
    def create(sound_name):
        return SoundButton(sound_name=sound_name)
