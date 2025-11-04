"""
Sound Manager Module
Handles all game audio including sound effects and background music.
"""

import pygame
import os


class SoundManager:
    """
    Manages sound effects and background music for the game.
    """

    def __init__(self, sounds_dir='assets/sounds'):
        """
        Initialize SoundManager.

        Args:
            sounds_dir: Directory containing sound files
        """
        pygame.mixer.init()
        self.sounds_dir = sounds_dir
        self.sounds = {}
        self.music_playing = False
        self.sound_enabled = True
        self.music_enabled = True
        self.volume = 0.7

        # Load sounds
        self._load_sounds()

    def _load_sounds(self):
        """Load all sound effects."""
        # Define sound file names
        sound_files = {
            'hit': 'hit.wav',
            'damage': 'damage.wav',
            'powerup': 'powerup.wav',
            'game_over': 'game_over.wav',
            'level_up': 'level_up.wav'
        }

        # Try to load each sound
        for sound_name, filename in sound_files.items():
            filepath = os.path.join(self.sounds_dir, filename)
            try:
                if os.path.exists(filepath):
                    self.sounds[sound_name] = pygame.mixer.Sound(filepath)
                    self.sounds[sound_name].set_volume(self.volume)
                else:
                    # Create a simple beep sound as placeholder
                    self.sounds[sound_name] = self._create_placeholder_sound(sound_name)
            except Exception as e:
                print(f"Warning: Could not load sound {sound_name}: {e}")
                self.sounds[sound_name] = None

    def _create_placeholder_sound(self, sound_type: str):
        """
        Create a simple placeholder sound.

        Args:
            sound_type: Type of sound to create

        Returns:
            pygame.mixer.Sound or None
        """
        try:
            # Create a simple square wave
            import numpy as np
            
            sample_rate = 22050
            duration = 0.1
            
            # Different frequencies for different sounds
            frequencies = {
                'hit': 880,      # A5 - high pitch
                'damage': 220,   # A3 - low pitch
                'powerup': 1320, # E6 - very high
                'game_over': 110, # A2 - very low
                'level_up': 660   # E5 - medium-high
            }
            
            frequency = frequencies.get(sound_type, 440)
            
            # Generate square wave
            t = np.linspace(0, duration, int(sample_rate * duration))
            wave = np.sin(2 * np.pi * frequency * t)
            
            # Add envelope (fade out)
            envelope = np.linspace(1, 0, len(wave))
            wave = wave * envelope
            
            # Convert to 16-bit
            wave = (wave * 32767).astype(np.int16)
            
            # Create stereo
            stereo_wave = np.column_stack((wave, wave))
            
            # Create pygame sound
            sound = pygame.sndarray.make_sound(stereo_wave)
            sound.set_volume(self.volume)
            return sound
        except Exception as e:
            print(f"Could not create placeholder sound: {e}")
            return None

    def play_sound(self, sound_name: str):
        """
        Play a sound effect.

        Args:
            sound_name: Name of the sound to play
        """
        if not self.sound_enabled:
            return

        if sound_name in self.sounds and self.sounds[sound_name]:
            try:
                self.sounds[sound_name].play()
            except Exception as e:
                print(f"Error playing sound {sound_name}: {e}")

    def play_music(self, music_file=None):
        """
        Play background music.

        Args:
            music_file: Path to music file (optional)
        """
        if not self.music_enabled:
            return

        try:
            if music_file and os.path.exists(music_file):
                pygame.mixer.music.load(music_file)
                pygame.mixer.music.set_volume(self.volume * 0.5)
                pygame.mixer.music.play(-1)  # Loop forever
                self.music_playing = True
        except Exception as e:
            print(f"Could not play music: {e}")

    def stop_music(self):
        """Stop background music."""
        if self.music_playing:
            pygame.mixer.music.stop()
            self.music_playing = False

    def toggle_sound(self):
        """Toggle sound effects on/off."""
        self.sound_enabled = not self.sound_enabled

    def toggle_music(self):
        """Toggle background music on/off."""
        self.music_enabled = not self.music_enabled
        if self.music_enabled and not self.music_playing:
            self.play_music()
        elif not self.music_enabled and self.music_playing:
            self.stop_music()

    def set_volume(self, volume: float):
        """
        Set master volume.

        Args:
            volume: Volume level (0.0 to 1.0)
        """
        self.volume = max(0.0, min(1.0, volume))
        
        # Update all sound volumes
        for sound in self.sounds.values():
            if sound:
                sound.set_volume(self.volume)
        
        # Update music volume
        if self.music_playing:
            pygame.mixer.music.set_volume(self.volume * 0.5)

    def cleanup(self):
        """Clean up pygame mixer."""
        self.stop_music()
        pygame.mixer.quit()
