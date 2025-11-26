"""Handles all game audio including sound effects and background music."""

import pygame
import os
from typing import Optional


class SoundManager:
    """Manages sound effects and background music for the game."""
    
    # Volume settings
    DEFAULT_SFX_VOLUME = 0.7
    DEFAULT_MUSIC_VOLUME = 0.4
    
    # Sound effect configurations
    SOUND_FILES = {
        'hit': 'hit.wav',
        'damage': 'damage.wav', 
        'powerup': 'powerup.wav',
        'game_over': 'game_over.wav',
        'level_up': 'level_up.wav',
        'button': 'button.wav',
        'countdown': 'countdown.mp3'
    }
    
    # Background music configurations
    MUSIC_FILES = {
        'menu': 'prologue.wav',
        'gameplay': 'battle.wav', # diganti jika sudah ada
    }

    def __init__(self, sounds_dir: str = 'assets/sounds', music_dir: str = 'assets/sounds') -> None:
        """Initialize sound manager with audio directories."""
        pygame.mixer.init()
        
        self.sounds_dir = sounds_dir
        self.music_dir = music_dir
        
        # Sound effects storage
        self.sounds = {}
        
        # Music state
        self.current_music = None
        self.music_files = {}
        
        # Settings
        self.sound_enabled = True
        self.music_enabled = True
        self.sfx_volume = self.DEFAULT_SFX_VOLUME
        self.music_volume = self.DEFAULT_MUSIC_VOLUME
        
        # Load assets
        self._load_sounds()
        self._load_music()

    def _load_sounds(self) -> None:
        """Load all sound effects."""
        for sound_name, filename in self.SOUND_FILES.items():
            filepath = os.path.join(self.sounds_dir, filename)
            
            try:
                if os.path.exists(filepath):
                    sound = pygame.mixer.Sound(filepath)
                    sound.set_volume(self.sfx_volume)
                    self.sounds[sound_name] = sound
                else:
                    print(f"[Warning] Sound file not found: {filepath}")
                    self.sounds[sound_name] = self._create_placeholder_sound(sound_name)
            except Exception as e:
                print(f"[Error] Could not load sound {sound_name}: {e}")
                self.sounds[sound_name] = None

    def _load_music(self) -> None:
        """Load and verify all music files."""
        for state, filename in self.MUSIC_FILES.items():
            filepath = os.path.join(self.music_dir, filename)
            
            if os.path.exists(filepath):
                self.music_files[state] = filepath
            else:
                print(f"[Warning] Music file not found: {filepath}")

    def _create_placeholder_sound(self, sound_type: str) -> Optional[pygame.mixer.Sound]:
        """Create simple placeholder sound effect."""
        try:
            import numpy as np
            
            sample_rate = 22050
            duration = 0.1
            
            # Different frequencies for different sounds
            frequencies = {
                'hit': 880,
                'damage': 220,
                'powerup': 1320,
                'game_over': 110,
                'level_up': 660,
                'button': 550
            }
            
            frequency = frequencies.get(sound_type, 440)
            
            # Generate square wave
            t = np.linspace(0, duration, int(sample_rate * duration))
            wave = np.sin(2 * np.pi * frequency * t)
            
            # Add fade-out envelope
            envelope = np.linspace(1, 0, len(wave))
            wave = wave * envelope
            
            # Convert to 16-bit stereo
            wave = (wave * 32767).astype(np.int16)
            stereo_wave = np.column_stack((wave, wave))
            
            sound = pygame.sndarray.make_sound(stereo_wave)
            sound.set_volume(self.sfx_volume)
            return sound
            
        except Exception as e:
            print(f"[Error] Could not create placeholder sound: {e}")
            return None

    # === SOUND EFFECTS ===

    def play_sound(self, sound_name: str) -> None:
        """Play sound effect by name."""
        if not self.sound_enabled:
            return

        if sound_name in self.sounds and self.sounds[sound_name]:
            try:
                self.sounds[sound_name].play()
            except Exception as e:
                print(f"[Error] Failed to play sound {sound_name}: {e}")

    # === BACKGROUND MUSIC ===
    
    def play_music(self, music_state: str, loops: int = -1, fade_ms: int = 0) -> None:
        """Play background music for game state."""
        if not self.music_enabled:
            return
        
        # Don't restart if same music is already playing
        if self.current_music == music_state and pygame.mixer.music.get_busy():
            return
        
        if music_state not in self.music_files:
            print(f"[Warning] Music state '{music_state}' not found")
            return
        
        try:
            pygame.mixer.music.load(self.music_files[music_state])
            pygame.mixer.music.set_volume(self.music_volume)
            pygame.mixer.music.play(loops=loops, fade_ms=fade_ms)
            self.current_music = music_state
            
        except Exception as e:
            print(f"[Error] Failed to play music '{music_state}': {e}")

    def stop_music(self, fade_ms: int = 0) -> None:
        """Stop currently playing music."""
        if fade_ms > 0:
            pygame.mixer.music.fadeout(fade_ms)
        else:
            pygame.mixer.music.stop()
        
        self.current_music = None

    def pause_music(self):
        """Pause current music."""
        pygame.mixer.music.pause()

    def unpause_music(self):
        """Resume paused music."""
        pygame.mixer.music.unpause()

    def crossfade_music(self, new_state: str, fade_out_ms=1000, fade_in_ms=1000):
        """
        Crossfade from current music to new music.

        Args:
            new_state: New game state
            fade_out_ms: Fade-out duration
            fade_in_ms: Fade-in duration
        """
        self.stop_music(fade_ms=fade_out_ms)
        pygame.time.wait(fade_out_ms)
        self.play_music(new_state, fade_ms=fade_in_ms)

    # === CONTROLS ===

    def toggle_sound(self):
        """Toggle sound effects on/off."""
        self.sound_enabled = not self.sound_enabled
        return self.sound_enabled

    def toggle_music(self):
        """Toggle background music on/off."""
        self.music_enabled = not self.music_enabled
        
        if not self.music_enabled:
            self.stop_music()
        
        return self.music_enabled

    def set_sfx_volume(self, volume: float) -> None:
        """Set sound effects volume (0.0 to 1.0)."""
        self.sfx_volume = max(0.0, min(1.0, volume))
        
        for sound in self.sounds.values():
            if sound:
                sound.set_volume(self.sfx_volume)

    def set_music_volume(self, volume: float) -> None:
        """Set background music volume (0.0 to 1.0)."""
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)

    def set_volume(self, volume: float) -> None:
        """Set master volume for both SFX and music (0.0 to 1.0)."""
        self.set_sfx_volume(volume)
        self.set_music_volume(volume)

    # === CLEANUP ===

    def cleanup(self) -> None:
        """Clean up pygame mixer."""
        try:
            if pygame.mixer.get_init():
                self.stop_music()
                pygame.mixer.quit()
        except:
            pass