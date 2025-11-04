"""
Cam-Fu - Pose Fighting Game
Main entry point for the game.
"""

import sys
from game_engine import GameEngine


def main():
    """
    Main entry point.
    """
    print("=" * 60)
    print("         CAM-FU - Pose Fighting Game")
    print("=" * 60)
    print()
    print("Welcome to Cam-Fu!")
    print("Use your body to fight! Punch targets and dodge obstacles.")
    print()
    print("Game Instructions:")
    print("  🎯 GREEN circles  = TARGETS (punch them for +10 points)")
    print("  💥 RED circles    = OBSTACLES (dodge them or lose HP!)")
    print("  ⭐ YELLOW circles = POWER-UPS (grab for bonuses)")
    print()
    print("Power-ups:")
    print("  🛡️  Shield       - Protects from damage (5s)")
    print("  ⚡ Double Score  - 2x points for targets (8s)")
    print("  🐌 Slow Motion  - Slows down objects (6s)")
    print()
    print("Controls:")
    print("  SPACE    - Pause/Resume")
    print("  C        - Toggle camera view")
    print("  R        - Restart (when game over)")
    print("  ESC / Q  - Quit game")
    print()
    print("=" * 60)
    print()
    
    # Ask for camera selection
    try:
        camera_input = input("Enter camera ID (0 for default, 1 for external): ").strip()
        camera_id = int(camera_input) if camera_input.isdigit() else 0
    except (ValueError, KeyboardInterrupt):
        print("\nUsing default camera (ID: 0)")
        camera_id = 0
    
    print()
    print("Starting game...")
    print()
    
    # Create and run game
    game = GameEngine(
        screen_width=1280,
        screen_height=720,
        camera_id=camera_id
    )
    
    try:
        game.run()
    except KeyboardInterrupt:
        print("\n\nGame interrupted by user")
    except Exception as e:
        print(f"\n\nError occurred: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("Thanks for playing Cam-Fu!")
    print("=" * 60)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
