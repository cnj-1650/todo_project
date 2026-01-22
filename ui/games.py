import pygame # type: ignore
import random
import customtkinter as ctk # type: ignore

class FlappyBirdGame:
    def __init__(self):
        pygame.init()
        self.screen_width = 400
        self.screen_height = 600
        self.bird_size = 30
        self.pipe_width = 60
        self.pipe_gap = 150
        
    def run(self):
        screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Task Master - Flappy Bird")
        clock = pygame.time.Clock()
        
        # Colors & Physics
        bird_y = self.screen_height // 2
        bird_x = 50
        gravity = 0.25
        bird_movement = 0
        
        pipes = []
        score = 0
        game_active = True

        # Timer for spawning pipes
        SPAWNPIPE = pygame.USEREVENT
        pygame.time.set_timer(SPAWNPIPE, 1200)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and game_active:
                        bird_movement = 0
                        bird_movement -= 6
                    if event.key == pygame.K_SPACE and not game_active:
                        game_active = True
                        pipes.clear()
                        bird_y = self.screen_height // 2
                        bird_movement = 0
                        score = 0
                if event.type == SPAWNPIPE and game_active:
                    pipe_height = random.randint(150, 400)
                    pipes.append(pygame.Rect(450, pipe_height, self.pipe_width, 600)) # Bottom pipe
                    pipes.append(pygame.Rect(450, 0, self.pipe_width, pipe_height - self.pipe_gap)) # Top

            screen.fill((52, 152, 219)) # Sky Blue

            if game_active:
                # Bird
                bird_movement += gravity
                bird_y += bird_movement
                bird_rect = pygame.Rect(bird_x, bird_y, self.bird_size, self.bird_size)
                pygame.draw.rect(screen, (241, 196, 15), bird_rect) # Yellow Bird

                # Pipes
                for pipe in pipes:
                    pipe.centerx -= 3
                    pygame.draw.rect(screen, (46, 204, 113), pipe)
                    if bird_rect.colliderect(pipe):
                        game_active = False

                pipes = [p for p in pipes if p.right > -50]

                # Boundaries
                if bird_y <= 0 or bird_y >= self.screen_height:
                    game_active = False
                
                score += 0.01
            else:
                font = pygame.font.SysFont("Arial", 30)
                text = font.render(f"Game Over! Score: {int(score)}", True, (255, 255, 255))
                screen.blit(text, (80, 250))
                subtext = font.render("Press SPACE to Restart", True, (255, 255, 255))
                screen.blit(subtext, (65, 300))

            pygame.display.update()
            clock.tick(120)