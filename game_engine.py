import pygame
import cv2
import numpy as np
import random
import mediapipe as mp

# Import modul eksternal
from pose_detector import PoseDetector
from collision_detector import CollisionDetector
from game_objects import Target, Obstacle, PowerUp
from score_manager import ScoreManager
from sound_manager import SoundManager
from renderer import GameRenderer
from spawn_manager import SpawnManager


class GameEngine:
    """
    Menangani logika inti game, update objek, dan deteksi tabrakan.
    Loop utama ditangani oleh main.py.
    """

    def __init__(self, screen, pose_detector, game_renderer, spawn_manager):
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()

        # Komponen eksternal
        self.pose_detector = pose_detector
        self.renderer = game_renderer
        self.spawn_manager = spawn_manager
        
        # Komponen internal
        self.collision_detector = CollisionDetector(collision_radius=25)
        self.score_manager = ScoreManager(starting_lives=3)
        self.sound_manager = SoundManager()

        # List objek game
        self.targets = []
        self.obstacles = []
        self.powerups = []
        
        # State
        self.paused = False
        self.mp_pose = mp.solutions.pose.PoseLandmark


    # RESET GAME
    def reset_game(self):
        """Reset seluruh state permainan."""
        print("Mereset game...")
        self.score_manager.reset()
        self.targets.clear()
        self.obstacles.clear()
        self.powerups.clear()
        self.spawn_manager.reset_timers()


    # UPDATE LOGIKA GAME
    def update(self, dt: float, landmarks):
        """Dipanggil setiap frame oleh main.py."""
        if self.paused or self.score_manager.game_over:
            return

        # Efek slow motion
        if self.score_manager.slow_motion_active:
            dt *= 0.5

        # Update timer powerup + spawn objek
        self.score_manager.update(dt)
        self.spawn_manager.update(dt, self.targets, self.obstacles, self.powerups)

        # Update semua objek
        for obj in self.targets: obj.update(dt)
        for obj in self.obstacles: obj.update(dt)
        for obj in self.powerups[:]:
            obj.update(dt)
            if not obj.active:
                self.powerups.remove(obj)

        # Deteksi tabrakan jika pose terdeteksi
        if landmarks:
            self.check_collisions(landmarks)

        # Bersihkan objek tak aktif
        self.targets = [t for t in self.targets if t.active]
        self.obstacles = [o for o in self.obstacles if o.active]


    # COLLISION HANDLING
    def check_collisions(self, landmarks):
        """Cek tabrakan tangan & badan dengan objek game."""

        # Titik tangan kiri & kanan (pergelangan)
        left_hand = [
            self.pose_detector.get_landmark_position(
                landmarks, self.mp_pose.LEFT_WRIST.value,
                self.screen_width, self.screen_height
            )
        ]
        right_hand = [
            self.pose_detector.get_landmark_position(
                landmarks, self.mp_pose.RIGHT_WRIST.value,
                self.screen_width, self.screen_height
            )
        ]

        # TABRAKAN TARGET (kena pukul)
        for target in self.targets[:]:
            if not target.active:
                continue

            hit = self.collision_detector.check_hand_collision(
                left_hand, right_hand, target.get_position(), target.radius
            )

            if hit:
                target.active = False
                self.score_manager.add_score(target.points, self.sound_manager)
                self.score_manager.targets_hit += 1
                self.sound_manager.play_sound('hit')

        # TABRAKAN POWERUP 
        for powerup in self.powerups[:]:
            if not powerup.active:
                continue

            hit = self.collision_detector.check_hand_collision(
                left_hand, right_hand, powerup.get_position(), powerup.radius
            )

            if hit:
                powerup.active = False
                self.score_manager.activate_powerup(powerup.type)
                self.sound_manager.play_sound('powerup')

        # TABRAKAN OBSTACLE (kena badan) 
        body_points = [
            self.pose_detector.get_landmark_position(landmarks, self.mp_pose.NOSE.value,
                self.screen_width, self.screen_height),
            self.pose_detector.get_landmark_position(landmarks, self.mp_pose.LEFT_SHOULDER.value,
                self.screen_width, self.screen_height),
            self.pose_detector.get_landmark_position(landmarks, self.mp_pose.RIGHT_SHOULDER.value,
                self.screen_width, self.screen_height),
        ]

        for obstacle in self.obstacles[:]:
            if not obstacle.active:
                continue

            if self.collision_detector.check_body_collision(
                body_points, obstacle.get_position(), obstacle.radius
            ):
                obstacle.active = False
                
                if self.score_manager.lose_life(self.sound_manager):
                    self.score_manager.subtract_score(obstacle.damage)


    # RENDERING
    def draw(self, landmarks):
        """Gambar objek game + UI (dipanggil setiap frame)."""
        self.renderer.draw_game_objects(self.targets, self.obstacles, self.powerups)

        if landmarks:
            self.renderer.draw_stickman(landmarks, self.pose_detector)

        self.renderer.draw_ui(self.score_manager, pygame.time.Clock())  # clock dummy


    # CLEANUP
    def cleanup(self):
        """Bersihkan resource."""
        print("Membersihkan GameEngine...")
        if self.pose_detector:
            self.pose_detector.close()
        self.sound_manager.cleanup()
        print("Cleanup selesai.")
