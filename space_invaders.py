import tkinter as tk
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
        
        # Create canvas
        self.canvas = tk.Canvas(root, width=self.WIDTH, height=self.HEIGHT, bg='black')
        self.canvas.pack()
        
        # Game state
        self.score = 0
        self.game_over = False
        self.aliens_moving_right = True  # Track alien movement direction
        
        # Create game objects
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
    
    def create_player(self):
        # Create player ship (triangle shape)
        x = self.WIDTH // 2
        y = self.HEIGHT - 50
        return self.canvas.create_polygon(
            x, y,
            x - 20, y + 40,
            x + 20, y + 40,
            fill='green'
        )
    
    def create_aliens(self):
        aliens = []
        rows = 5
        cols = 8
        for row in range(rows):
            for col in range(cols):
                x = 100 + col * 80
                y = 50 + row * 60
                alien = self.canvas.create_oval(
                    x, y,
                    x + 40, y + 40,
                    fill='red'
                )
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
            self.canvas.move(self.player, -self.PLAYER_SPEED, 0)
    
    def move_player_right(self, event):
        if not self.game_over:
            self.canvas.move(self.player, self.PLAYER_SPEED, 0)
    
    def shoot(self, event):
        if not self.game_over:
            # Get the current position of the player (triangle has 6 coordinates)
            coords = self.canvas.coords(self.player)
            # Get the top point of the triangle (first two coordinates)
            x = coords[0]
            y = coords[1]
            # Create bullet at the top center of the player
            bullet = self.canvas.create_rectangle(
                x, y,
                x, y - 10,
                fill='yellow',
                outline='yellow'  # Add yellow outline
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
                    x1, y1, x2, y2 = self.canvas.coords(alien)
                    if x2 > self.WIDTH - 10:
                        self.aliens_moving_right = False
                        break
                    elif x1 < 10:
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
            # Randomly select an alien to shoot
            shooter = random.choice(self.aliens)
            x1, y1, x2, y2 = self.canvas.coords(shooter)
            bullet = self.canvas.create_rectangle(
                x1 + 20, y2,
                x1 + 20, y2 + 10,
                fill='white',
                outline='white'  # Add white outline
            )
            self.alien_bullets.append(bullet)
    
    def check_collisions(self):
        # Check player bullets hitting aliens
        for bullet in self.player_bullets[:]:
            bullet_coords = self.canvas.coords(bullet)
            for alien in self.aliens[:]:
                alien_coords = self.canvas.coords(alien)
                if self.check_overlap(bullet_coords, alien_coords):
                    self.canvas.delete(bullet)
                    self.canvas.delete(alien)
                    self.player_bullets.remove(bullet)
                    self.aliens.remove(alien)
                    self.score += 100
                    break
        
        # Check alien bullets hitting player
        player_coords = self.canvas.coords(self.player)
        for bullet in self.alien_bullets[:]:
            bullet_coords = self.canvas.coords(bullet)
            # Check if bullet is within the player's triangle bounds
            if self.check_overlap(bullet_coords, player_coords):
                self.game_over = True
                # Clear all game objects
                for bullet in self.player_bullets:
                    self.canvas.delete(bullet)
                for bullet in self.alien_bullets:
                    self.canvas.delete(bullet)
                for alien in self.aliens:
                    self.canvas.delete(alien)
                for barrier in self.barriers:
                    self.canvas.delete(barrier)
                # Show game over message
                self.canvas.create_text(
                    self.WIDTH/2, self.HEIGHT/2,
                    text="GAME OVER!",
                    fill='white',
                    font=('Arial', 48)
                )
                # Show final score
                self.canvas.create_text(
                    self.WIDTH/2, self.HEIGHT/2 + 50,
                    text=f"Score: {self.score}",
                    fill='white',
                    font=('Arial', 24)
                )
                break
    
    def check_overlap(self, coords1, coords2):
        # For rectangle (bullet) and polygon (player) collision
        if len(coords2) == 6:  # Player is a triangle
            # Get the bounding box of the player's triangle
            min_x = min(coords2[0], coords2[2], coords2[4])
            max_x = max(coords2[0], coords2[2], coords2[4])
            min_y = min(coords2[1], coords2[3], coords2[5])
            max_y = max(coords2[1], coords2[3], coords2[5])
            
            # Check if bullet is within the bounding box
            return not (coords1[2] < min_x or
                       coords1[0] > max_x or
                       coords1[3] < min_y or
                       coords1[1] > max_y)
        else:  # Both are rectangles
            return not (coords1[2] < coords2[0] or
                       coords1[0] > coords2[2] or
                       coords1[3] < coords2[1] or
                       coords1[1] > coords2[3])

if __name__ == "__main__":
    root = tk.Tk()
    game = SpaceInvaders(root)
    root.mainloop() 