import sys
import cv2
import pygame as game
import random
import time

class Game:
    def __init__(self, height=650, width=550):
        game.init()
        game.mixer.init()
        self.WIDTH = width
        self.HEIGHT = height
        self.bullets = []  # Player bullets
        self.bot_bullets = []  # Bot bullets
        self.player_pos = game.Vector2(width / 2 + 100, 380)  # Player position
        self.cap = cv2.VideoCapture('space.mp4')
        # Bullet dimensions
        self.bullet_width = 3
        self.bullet_height = 8
        # Create bots and store them in self.bots
        self.bots = self.create_bots()
        self.player_image = game.image.load('player.png')
        self.player_image = game.transform.scale(self.player_image, (50, 50))

        self.enemy_image = game.image.load('enemy.png')
        self.enemy_image = game.transform.scale(self.enemy_image, (50, 50))

        # Load sounds
        self.shooting_sound = game.mixer.Sound('shoot.wav')
        self.movement_sound = game.mixer.Sound('move.wav')

        screen = game.display.set_mode((height, width))
        clock = game.time.Clock()
        game.mixer.music.load('song.mpeg')
        game.mixer.music.play(loops=-1)

        running = True
        while running:
            for event in game.event.get():
                if event.type == game.QUIT:
                    running = False

                self.shooting(event)
                self.movement(event)

            self.video(screen)
            self.player(screen)  # Draw player
            self.draw_bots(screen)  # Draw bots
            self.line(screen)
            self.update_bullets(screen)  # Update player bullets
            self.update_bot_bullets(screen)  # Update bot bullets
            self.bot_shoot()  # Bots shoot bullets randomly

            if not self.bots:
                print('You Won')
                game.mixer.music.load('victory.wav')
                game.mixer.music.play()
                time.sleep(3)
                running = False

            game.display.flip()
            clock.tick(60)

        self.quit_game()
    def player(self, screen):
        player_rect = self.player_image.get_rect(center = (self.player_pos.x, self.player_pos.y))
        screen.blit(self.player_image, player_rect)

    def movement(self, event, move_distance=100):
        # Handle player movement with left and right keys
        if event.type == game.KEYDOWN:
            if event.key == game.K_d and self.player_pos.x < self.WIDTH - 20:
                self.player_pos.x += move_distance
                # game.mixer.music.load('move.wav')
                self.movement_sound.play()
            elif event.key == game.K_a and self.player_pos.x > 130:
                # game.mixer.music.load('move.wav')
                self.movement_sound.play()
                self.player_pos.x -= move_distance

    def create_bots(self, bot_radius=20):
        # Create bots with their positions in a grid pattern
        bot_positions = [
            game.Vector2(50, 50), game.Vector2(50, 150), game.Vector2(50, 250),
            game.Vector2(150, 50), game.Vector2(150, 150), game.Vector2(150, 250),
            game.Vector2(250, 50), game.Vector2(250, 150), game.Vector2(250, 250),
            game.Vector2(350, 50), game.Vector2(350, 150), game.Vector2(350, 250),
            game.Vector2(450, 50), game.Vector2(450, 150), game.Vector2(450, 250),
            game.Vector2(550, 50), game.Vector2(550, 150), game.Vector2(550, 250),
        ]
        bots = []
        for pos in bot_positions:
            bot_rect = game.Rect(pos.x, pos.y, bot_radius * 2, bot_radius * 2)
            bots.append({'rect': bot_rect})  # Store the rect of each bot
        return bots

    def draw_bots(self, screen):
        # Draw each bot using its position from self.bots
        for bot in self.bots:
            bot_rect = self.enemy_image.get_rect(center = bot['rect'].center)  # Get the center of each bot rect
            screen.blit(self.enemy_image, bot_rect)
    def video(self, screen):
        ret, frame = self.cap.read()
        if not ret:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Restart the video if it ends
            ret, frame = self.cap.read()

        # Convert the video frame to Pygame surface
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert BGR (OpenCV) to RGB (Pygame)
        frame = cv2.resize(frame, (self.HEIGHT, self.WIDTH))  # Resize to match screen size
        frame_surface = game.surfarray.make_surface(frame.swapaxes(0, 1))

        # Draw the video frame as the background
        screen.blit(frame_surface, (0, 0))

    def line(self, screen):
        # Draw a line for separating the game space
        game.draw.line(screen, 'white', width=6, start_pos=(30, 420), end_pos=(625, 420))

    def shooting(self, event):
        if event.type == game.KEYDOWN:
            if event.key == game.K_SPACE:
                # Create a bullet at the player's position (center top of the player)
                bullet_rect = game.Rect(self.player_pos.x, self.player_pos.y - 20, self.bullet_width, self.bullet_height)
                self.bullets.append(bullet_rect)
                self.shooting_sound.play()

    def update_bullets(self, screen):
        # Move bullets upwards and check for collisions
        for bullet in self.bullets[:]:
            bullet.y -= 5  # Bullet speed
            game.draw.rect(screen, 'red', bullet)  # Draw bullet

            # Check collision with bots
            for bot in self.bots[:]:
                if bullet.colliderect(bot['rect']):
                    self.bullets.remove(bullet)  # Remove bullet
                    self.bots.remove(bot)  # Remove bot on collision
                    break  # Exit loop since bullet is removed

            # Remove bullet if it goes off-screen
            if bullet.bottom < 0:
                self.bullets.remove(bullet)

    def bot_shoot(self):
        # Randomly make a bot shoot bullets downwards
        if len(self.bots) > 0 and random.randint(0, 50) == 1:  # 1/50 chance per frame
            shooting_bot = random.choice(self.bots)  # Random bot shoots
            bullet_rect = game.Rect(shooting_bot['rect'].centerx, shooting_bot['rect'].bottom, self.bullet_width, self.bullet_height)
            self.bot_bullets.append(bullet_rect)

    def update_bot_bullets(self, screen):
        # Move bot bullets downwards and check for collision with player
        for bullet in self.bot_bullets[:]:
            bullet.y += 5  # Bullet speed
            game.draw.rect(screen, 'white', bullet)  # Draw bot bullet

            # Check collision with player
            player_rect = game.Rect(self.player_pos.x - 20, self.player_pos.y - 20, 40, 40)
            if bullet.colliderect(player_rect):
                game.mixer.music.load('death.wav')
                game.mixer.music.play()
                print("You Lost")
                time.sleep(3)
                sys.exit()

            # Remove bullet if it goes off-screen
            if bullet.top > self.HEIGHT:
                self.bot_bullets.remove(bullet)

    def quit_game(self):
        self.cap.release()
        game.quit()

Game()