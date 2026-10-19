import os
import pygame
from config import (SOUNDS_DIR, MENU_MUSIC_VOLUME, GAME_MUSIC_VOLUME,
                    MUSIC_FADE_SPEED, MUSIC_DUCK_AMOUNT, MUSIC_DUCK_SPEED,
                    MUSIC_UNDUCK_SPEED, MUSIC_MUTE_SPEED)

class SoundManager:
    def __init__(self):
        self.enabled = False
        self.is_muted = False
        self.sounds = {}
        self.music_channels = {}
        self.music_volumes = {"menu": 0.0, "game": 0.0}
        self.music_mode = "menu"
        self.duck_current = 1.0
        self.duck_target = 1.0
        try:
            pygame.mixer.init()
            self.enabled = True
        except Exception:
            self.enabled = False
        self._load_all()
        self._load_music()

    def toggle_mute(self):
        self.is_muted = not self.is_muted

    def _load_all(self):
        if not os.path.exists(SOUNDS_DIR):
            os.makedirs(SOUNDS_DIR, exist_ok=True)
        for name in ("move", "win", "lose", "select"):
            for ext in (".wav", ".ogg", ".mp3"):
                path = os.path.join(SOUNDS_DIR, name + ext)
                if os.path.exists(path):
                    try:
                        self.sounds[name] = pygame.mixer.Sound(path)
                        break
                    except Exception:
                        pass

    def _load_music(self):
        if not self.enabled:
            return
        try:
            pygame.mixer.set_num_channels(8)
        except Exception:
            pass
        try:
            pygame.mixer.set_reserved(3)
        except Exception:
            pass
        channel_ids = {"menu": 1, "game": 2}
        for key, name in (("menu", "menu_music"), ("game", "game_music")):
            for ext in (".ogg", ".mp3", ".wav"):
                path = os.path.join(SOUNDS_DIR, name + ext)
                if os.path.exists(path):
                    try:
                        sound = pygame.mixer.Sound(path)
                        channel = pygame.mixer.Channel(channel_ids[key])
                        channel.play(sound, loops=-1)
                        channel.set_volume(0.0)
                        self.music_channels[key] = channel
                        break
                    except Exception:
                        pass

    def play(self, name):
        if not self.enabled or self.is_muted:
            return
        sound = self.sounds.get(name)
        if sound is not None:
            sound.play()

    def set_music_mode(self, mode):
        self.music_mode = mode

    def duck_music(self):
        self.duck_target = MUSIC_DUCK_AMOUNT

    def unduck_music(self):
        self.duck_target = 1.0

    def update(self, dt):
        if not self.enabled:
            return

        if self.duck_current < self.duck_target:
            self.duck_current = min(self.duck_target, self.duck_current + MUSIC_UNDUCK_SPEED * dt)
        elif self.duck_current > self.duck_target:
            self.duck_current = max(self.duck_target, self.duck_current - MUSIC_DUCK_SPEED * dt)

        menu_target = 0.0
        game_target = 0.0
        if not self.is_muted:
            if self.music_mode == "menu":
                menu_target = MENU_MUSIC_VOLUME
            elif self.music_mode == "game":
                game_target = GAME_MUSIC_VOLUME * self.duck_current

        fade_speed = MUSIC_MUTE_SPEED if self.is_muted else MUSIC_FADE_SPEED

        for key, channel in self.music_channels.items():
            target = menu_target if key == "menu" else game_target
            current = self.music_volumes[key]
            if current < target:
                current = min(target, current + fade_speed * dt)
            elif current > target:
                current = max(target, current - fade_speed * dt)
            self.music_volumes[key] = current
            try:
                channel.set_volume(current)
            except Exception:
                pass