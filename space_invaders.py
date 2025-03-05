import tkinter as tk
from PIL import Image, ImageTk
import random
import time

class SpaceInvaders:
    def __init__(self, root):
        self.root = root
        self.root.title("Space Invaders")
        
        # Game constants
        self.WIDTH = 800
        self.HEIGHT = 600
        self.PLAYER_SPEED = 5
        self.BULLET_SPEED = 7
        self.ALIEN_SPEED = 2
        self.ALIEN_BULLET_SPEED = 4
        self.ALIEN_SHOOT_INTERVAL = 5  # seconds
        self.PLAYER_SIZE = 50
        self.ALIEN_SIZE = 40
        self.EXPLOSION_DURATION = 20  # milliseconds
        self.ZAP_WIDTH = 8  # Narrow width for alien bullets
        self.ZAP_HEIGHT = 20  # Taller height for alien bullets
        
        # Load and resize images
        self.player_image = self.load_and_resize_image("si_player.png", (self.PLAYER_SIZE, self.PLAYER_SIZE))
        self.explosion_image = self.load_and_resize_image("si_explode.png", (self.ALIEN_SIZE, self.ALIEN_SIZE))
        self.zap_image = self.load_and_resize_image("si_zap.png", (self.ZAP_WIDTH, self.ZAP_HEIGHT))
        self.alien_images = [
            self.load_and_resize_image("si_alien1.png", (self.ALIEN_SIZE, self.ALIEN_SIZE)),
            self.load_and_resize_image("si_alien2.png", (self.ALIEN_SIZE, self.ALIEN_SIZE)),
            self.load_and_resize_image("si_alien3.png", (self.ALIEN_SIZE, self.ALIEN_SIZE)),
            self.load_and_resize_image("si_alien4.png", (self.ALIEN_SIZE, self.ALIEN_SIZE)),
            self.load_and_resize_image("si_alien5.png", (self.ALIEN_SIZE, self.ALIEN_SIZE))
        ]
        
        # Create canvas
        self.canvas = tk.Canvas(root, width=self.WIDTH, height=self.HEIGHT, bg='black')
        self.canvas.pack()
        
        # Game state
        self.score = 0
        self.game_over = False
        self.aliens_moving_right = True
        
        # Create game objects
        self.score_display = self.create_score_display()
        self.player = self.create_player()
        self.aliens = self.create_aliens()
        self.barriers = self.create_barriers()
        self.player_bullets = []
        self.alien_bullets = []
        
        # Bind controls
        self.root.bind('<Left>', self.move_player_left)
        self.root.bind('<Right>', self.move_player_right)
        self.root.bind('<space>', self.shoot)
        
        # Start game loop
        self.last_alien_shot = time.time()
        self.update()
    
    def load_and_resize_image(self, filename, size):
        image = Image.open(filename)
        image = image.resize(size, Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(image)
    
    def create_score_display(self):
        return self.canvas.create_text(
            10, 10,
            text="Score: 0",
            fill='white',
            font=('Arial', 20),
            anchor='nw'
        )
    
    def update_score_display(self):
        self.canvas.itemconfig(self.score_display, text=f"Score: {self.score}")
    
    def create_player(self):
        x = self.WIDTH // 2 - 25  # Adjust for image size
        y = self.HEIGHT - 100
        return self.canvas.create_image(x, y, image=self.player_image, anchor='nw')
    
    def create_aliens(self):
        aliens = []
        rows = 5
        cols = 8
        for row in range(rows):
            alien_image = self.alien_images[row % len(self.alien_images)]
            for col in range(cols):
                x = 100 + col * 80
                y = 50 + row * 60
                alien = self.canvas.create_image(x, y, image=alien_image, anchor='nw')
                aliens.append(alien)
        return aliens
    
    def create_barriers(self):
        barriers = []
        for i in range(3):
            x = 200 + i * 200
            y = self.HEIGHT - 150
            barrier = self.canvas.create_rectangle(
                x, y,
                x + 100, y + 40,
                fill='gray'
            )
            barriers.append(barrier)
        return barriers
    
    def move_player_left(self, event):
        if not self.game_over:
            coords = self.canvas.coords(self.player)
            if coords[0] > 0:  # Check left boundary
                self.canvas.move(self.player, -self.PLAYER_SPEED, 0)
    
    def move_player_right(self, event):
        if not self.game_over:
            coords = self.canvas.coords(self.player)
            if coords[0] < self.WIDTH - 50:  # Check right boundary
                self.canvas.move(self.player, self.PLAYER_SPEED, 0)
    
    def shoot(self, event):
        if not self.game_over:
            coords = self.canvas.coords(self.player)
            # Create bullet at the top center of the player
            bullet = self.canvas.create_rectangle(
                coords[0] + 25, coords[1],  # Center of player
                coords[0] + 25, coords[1] - 10,
                fill='yellow',
                outline='yellow'
            )
            self.player_bullets.append(bullet)
    
    def update(self):
        if not self.game_over:
            # Move player bullets
            for bullet in self.player_bullets[:]:
                self.canvas.move(bullet, 0, -self.BULLET_SPEED)
                if self.canvas.coords(bullet)[3] < 0:
                    self.canvas.delete(bullet)
                    self.player_bullets.remove(bullet)
            
            # Move aliens side to side
            if self.aliens:
                # Check if any alien has reached the edge
                for alien in self.aliens:
                    coords = self.canvas.coords(alien)
                    x = coords[0]  # x coordinate
                    if x + 40 > self.WIDTH - 10:  # Add alien width for right boundary
                        self.aliens_moving_right = False
                        break
                    elif x < 10:
                        self.aliens_moving_right = True
                        break
                
                # Move all aliens in the current direction
                for alien in self.aliens:
                    if self.aliens_moving_right:
                        self.canvas.move(alien, self.ALIEN_SPEED, 0)
                    else:
                        self.canvas.move(alien, -self.ALIEN_SPEED, 0)
            
            # Alien shooting
            current_time = time.time()
            if current_time - self.last_alien_shot >= self.ALIEN_SHOOT_INTERVAL:
                self.alien_shoot()
                self.last_alien_shot = current_time
            
            # Move alien bullets
            for bullet in self.alien_bullets[:]:
                self.canvas.move(bullet, 0, self.ALIEN_BULLET_SPEED)
                if self.canvas.coords(bullet)[1] > self.HEIGHT:
                    self.canvas.delete(bullet)
                    self.alien_bullets.remove(bullet)
            
            # Check collisions
            self.check_collisions()
            
            # Schedule next update
            self.root.after(16, self.update)  # approximately 60 FPS
    
    def alien_shoot(self):
        if self.aliens:
            shooter = random.choice(self.aliens)
            coords = self.canvas.coords(shooter)
            # Create zap at the bottom center of the alien
            bullet = self.canvas.create_image(
                coords[0] + (self.ALIEN_SIZE - self.ZAP_WIDTH)//2,  # Center the narrow zap
                coords[1] + self.ALIEN_SIZE - 5,  # Slightly overlap with alien
                image=self.zap_image,
                anchor='nw'
            )
            self.alien_bullets.append(bullet)
    
    def show_explosion(self, x, y, alien_to_remove):
        # Create explosion at alien's position
        explosion = self.canvas.create_image(x, y, image=self.explosion_image, anchor='nw')
        # Schedule cleanup
        self.root.after(self.EXPLOSION_DURATION, lambda: self.remove_explosion(explosion, alien_to_remove))
    
    def remove_explosion(self, explosion, alien):
        self.canvas.delete(explosion)  # Remove explosion image
        self.canvas.delete(alien)      # Remove the alien
        self.aliens.remove(alien)      # Remove from list
    
    def check_collisions(self):
        # Check player bullets hitting aliens or barriers
        for bullet in self.player_bullets[:]:
            bullet_coords = self.canvas.coords(bullet)
            
            # Check collision with aliens
            for alien in self.aliens[:]:
                alien_coords = self.canvas.coords(alien)
                if self.check_overlap(bullet_coords, alien_coords, self.ALIEN_SIZE):
                    self.canvas.delete(bullet)
                    self.player_bullets.remove(bullet)
                    # Show explosion instead of immediately removing alien
                    self.show_explosion(alien_coords[0], alien_coords[1], alien)
                    self.score += 100
                    self.update_score_display()
                    break
            
            # Check collision with barriers
            for barrier in self.barriers[:]:
                barrier_coords = self.canvas.coords(barrier)
                if self.check_overlap(bullet_coords, barrier_coords):
                    self.canvas.delete(bullet)
                    self.player_bullets.remove(bullet)
                    # Damage the barrier (make it smaller or remove if too damaged)
                    self.damage_barrier(barrier)
                    break
        
        # Check alien bullets hitting player or barriers
        for bullet in self.alien_bullets[:]:
            bullet_coords = self.canvas.coords(bullet)
            
            # Check collision with player
            player_coords = self.canvas.coords(self.player)
            if self.check_overlap(bullet_coords, player_coords, self.PLAYER_SIZE):
                self.end_game("GAME OVER!")
                break
            
            # Check collision with barriers
            for barrier in self.barriers[:]:
                barrier_coords = self.canvas.coords(barrier)
                if self.check_overlap(bullet_coords, barrier_coords):
                    self.canvas.delete(bullet)
                    self.alien_bullets.remove(bullet)
                    self.damage_barrier(barrier)
                    break
        
        self.check_win()
    
    def damage_barrier(self, barrier):
        coords = self.canvas.coords(barrier)
        width = coords[2] - coords[0]
        if width > 20:  # If barrier is still big enough to be damaged
            # Make the barrier smaller
            new_width = width - 10
            self.canvas.coords(barrier,
                             coords[0] + 5, coords[1],
                             coords[0] + new_width - 5, coords[3])
        else:
            # Remove the barrier if it's too damaged
            self.canvas.delete(barrier)
            self.barriers.remove(barrier)
    
    def end_game(self, message):
        self.game_over = True
        # Clear all game objects
        for obj in self.player_bullets + self.alien_bullets + self.aliens + self.barriers:
            self.canvas.delete(obj)
        # Show game over message
        self.canvas.create_text(
            self.WIDTH/2, self.HEIGHT/2,
            text=message,
            fill='white',
            font=('Arial', 48)
        )
        self.canvas.create_text(
            self.WIDTH/2, self.HEIGHT/2 + 50,
            text=f"Final Score: {self.score}",
            fill='white',
            font=('Arial', 24)
        )
    
    def check_win(self):
        if not self.aliens and not self.game_over:
            self.game_over = True
            self.canvas.create_text(
                self.WIDTH/2, self.HEIGHT/2,
                text="YOU WIN!",
                fill='white',
                font=('Arial', 48)
            )
            self.canvas.create_text(
                self.WIDTH/2, self.HEIGHT/2 + 50,
                text=f"Final Score: {self.score}",
                fill='white',
                font=('Arial', 24)
            )
    
    def check_overlap(self, coords1, coords2, target_size=None):
        # For collision detection between rectangles or images
        # Handle different types of objects (bullets, zaps, aliens, player)
        if len(coords1) > 2:  # Rectangle (player bullet)
            obj1_left = coords1[0]
            obj1_right = coords1[2]
            obj1_top = coords1[1]
            obj1_bottom = coords1[3]
        else:  # Image (zap, alien, or player)
            obj1_left = coords1[0]
            obj1_top = coords1[1]
            if target_size:  # For player or alien
                obj1_right = coords1[0] + target_size
                obj1_bottom = coords1[1] + target_size
            else:  # For zap
                obj1_right = coords1[0] + self.ZAP_WIDTH
                obj1_bottom = coords1[1] + self.ZAP_HEIGHT

        # Similar handling for the second object
        if len(coords2) > 2:  # Rectangle (barrier)
            obj2_left = coords2[0]
            obj2_right = coords2[2]
            obj2_top = coords2[1]
            obj2_bottom = coords2[3]
        else:  # Image (alien or player)
            obj2_left = coords2[0]
            obj2_top = coords2[1]
            if target_size:  # For player or alien
                obj2_right = coords2[0] + target_size
                obj2_bottom = coords2[1] + target_size
            else:  # This case shouldn't occur but handle it anyway
                obj2_right = coords2[0] + self.ALIEN_SIZE
                obj2_bottom = coords2[1] + self.ALIEN_SIZE
        
        return not (obj1_right < obj2_left or
                   obj1_left > obj2_right or
                   obj1_bottom < obj2_top or
                   obj1_top > obj2_bottom)

if __name__ == "__main__":
    root = tk.Tk()
    game = SpaceInvaders(root)
    root.mainloop() 