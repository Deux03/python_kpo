import pygame
import sys
import os
import random


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Fruit Nija")
        self.current_resolution = (1400, 800)
        self.screen = pygame.display.set_mode(self.current_resolution)
        self.clock = pygame.time.Clock()
        self.fruits = []
        self.fruit_types = ['watermelon', 'apple', 'banana']
        self.speed_increase_interval = 5000
        self.last_speed_increase_time = pygame.time.get_ticks()
        self.fruit_speed = -1
        self.score = 0
        self.lives = 3
        self.game_over = False
        self.end_time = None
        self.game_started = False
        self.start_ticks = None
        self.buttons_rects = {
            'restart_button_rect': pygame.Rect(self.current_resolution[0] // 2 - 100,
                                               self.current_resolution[1] // 2 + 100, 200, 50),
            'start_button_rect': pygame.Rect(self.current_resolution[0] // 2 - 100, self.current_resolution[1] // 2,
                                             200, 50),
            'settings_button_rect': pygame.Rect(self.current_resolution[0] // 2 - 100,
                                                self.current_resolution[1] // 2 + 100, 200, 50),
            'quit_button_rect': pygame.Rect(self.current_resolution[0] // 2 - 100,
                                            self.current_resolution[1] // 2 + 200, 200, 50)
        }
        try:
            self.font = pygame.font.Font('fonts/comic.ttf', 30)
        except FileNotFoundError:
            print("Font file 'fonts/comic.ttf' not found, using default font.")
            self.font = pygame.font.Font(None, 30)
        self.ig_background_image = self.load_and_scale_image('background/background.jpg', self.current_resolution)
        self.start_bg_img = self.load_and_scale_image('background/WelcomeScreen.jpg', self.current_resolution)
        self.background_img = self.start_bg_img

    def load_and_scale_image(self, filepath, size):
        """
           Loads an image from filepath and scales it to the specified size.
           If loading fails, returns a simple black surface of the specified size.
           """
        try:
            image = pygame.image.load(filepath).convert()
            return pygame.transform.scale(image, size)
        except FileNotFoundError:
            print(f"Error loading image {filepath}, using a black background instead.")
            return pygame.Surface(size)

    def reset_game(self):
        self.last_speed_increase_time = pygame.time.get_ticks()
        self.fruit_speed = -1
        self.score = 0
        self.lives = 3
        self.game_over = False
        self.end_time = None
        self.game_started = False
        self.fruits = []
        self.background_img = self.start_bg_img

    def display_pause(self):
        pause_text = self.font.render(f'P - pause', True, (255, 255, 255))
        self.screen.blit(pause_text, (self.current_resolution[0] - 150, 10))

    def display_timer(self, current_time, start_time, dest_x=10, dest_y=10, color=(255, 255, 255)):
        elapsed_time = (current_time - start_time) / 1000
        timer_text = self.font.render(f'Time: {elapsed_time:.2f}s', True, color)
        self.screen.blit(timer_text, (dest_x, dest_y))

    def display_score(self):
        score_text = self.font.render(f'Score: {self.score}', True, (255, 255, 255))
        self.screen.blit(score_text, (10, 50))

    def display_lives(self):
        lives_text = self.font.render(f'Lives: {self.lives}', True, (255, 255, 255))
        self.screen.blit(lives_text, (10, 90))

    def display_fps(self):
        fps_text = self.font.render(f'FPS: {self.clock.get_fps():.0f}', True, (255, 255, 255))
        self.screen.blit(fps_text, (10, 130))

    def display_game_over(self):
        u_lost_text = self.font.render(f'YOU LOST!', True, (255, 0, 0))
        self.screen.blit(u_lost_text, (self.current_resolution[0] // 2 - 100, self.current_resolution[1] // 2 - 100))
        total_score = self.font.render(f'Total score: {self.score}', True, (255, 0, 0))
        self.screen.blit(total_score, (self.current_resolution[0] // 2 - 100, self.current_resolution[1] // 2 - 50))
        timer_text = self.font.render(f'Time: {self.end_time:.2f}s', True, (255, 0, 0))
        self.screen.blit(timer_text, (self.current_resolution[0] // 2 - 100, self.current_resolution[1] // 2))

    def display_button(self, mouse_x, mouse_y, btn_rect, text):
        hover = btn_rect.collidepoint(mouse_x, mouse_y)
        if hover:
            button_color = (0, 200, 0)
        else:
            button_color = (255, 0, 0)
        pygame.draw.rect(self.screen, button_color, btn_rect)
        button_text = self.font.render(text, True, (255, 255, 255))
        text_rect = button_text.get_rect(center=btn_rect.center)
        self.screen.blit(button_text, text_rect)

    def speed_increaser(self, current_time):
        if current_time - self.last_speed_increase_time > self.speed_increase_interval:
            self.fruit_speed -= 1.05
            self.last_speed_increase_time = current_time

    def fruits_movement(self, mouse_x, mouse_y):
        for fruit in self.fruits[:]:
            fruit.y_pos += self.fruit_speed
            fruit.img_pos = [fruit.x_pos, fruit.y_pos]

            fruit_rect = pygame.Rect(fruit.x_pos, fruit.y_pos, 100, 100)

            if fruit_rect.collidepoint(mouse_x, mouse_y):
                self.fruits.remove(fruit)
                self.score += 1
                continue

            self.screen.blit(fruit.img, fruit.img_pos)
            if fruit.y_pos < -100:
                self.fruits.remove(fruit)
                self.lives -= 1

    def spawn_random_fruits(self):
        if random.randint(0, 40) == 0:
            fruit_type = random.choice(self.fruit_types)
            self.fruits.append(Fruit(fruit_type, self.fruit_speed))

    def close_game(self):
        pygame.quit()
        sys.exit()

    def run_game(self):
        pygame.mouse.set_visible(0)

        while True:
            self.screen.blit(self.background_img, (0, 0))
            current_ticks = pygame.time.get_ticks()
            mouse_x, mouse_y = pygame.mouse.get_pos()

            if not self.game_started:
                self.display_button(mouse_x, mouse_y, self.buttons_rects['start_button_rect'], "START")
                self.display_button(mouse_x, mouse_y, self.buttons_rects['settings_button_rect'], "SETTINGS")
                self.display_button(mouse_x, mouse_y, self.buttons_rects['quit_button_rect'], "QUIT")
            else:
                if self.lives <= 0 and not self.game_over:
                    self.game_over = True
                    self.end_time = (current_ticks - self.start_ticks) / 1000

                if not self.game_over:
                    self.speed_increaser(current_ticks)
                    self.display_timer(current_ticks, self.start_ticks)
                    self.display_score()
                    self.display_lives()
                    self.display_fps()
                    self.display_pause()
                    self.fruits_movement(mouse_x, mouse_y)
                    self.spawn_random_fruits()
                else:
                    self.display_game_over()
                    self.display_button(mouse_x, mouse_y, self.buttons_rects['restart_button_rect'], "MENU")
                    self.display_button(mouse_x, mouse_y, self.buttons_rects['quit_button_rect'], "QUIT")

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.close_game()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.buttons_rects['restart_button_rect'].collidepoint(mouse_x, mouse_y):
                        self.reset_game()

                    elif self.buttons_rects['settings_button_rect'].collidepoint(mouse_x, mouse_y):
                        self.display_settings()

                    elif self.buttons_rects['quit_button_rect'].collidepoint(mouse_x, mouse_y):
                        self.close_game()

                    elif self.buttons_rects['start_button_rect'].collidepoint(mouse_x, mouse_y):
                        if not self.game_started:
                            self.game_started = True
                            self.start_ticks = pygame.time.get_ticks()
                            self.background_img = self.ig_background_image

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p and not self.game_over:
                        self.pause_game()

            pygame.draw.circle(self.screen, (255, 0, 0), (mouse_x, mouse_y), 5)
            pygame.display.flip()
            self.clock.tick(60)

    def display_settings(self):
        pass

    def pause_game(self):
        paused = True
        while paused:
            self.screen.blit(self.background_img, (0, 0))
            mouse_x, mouse_y = pygame.mouse.get_pos()
            pause_text = self.font.render("Game paused, press 'P' to unpause", True, (255, 255, 255))
            self.screen.blit(pause_text, (self.current_resolution[0] // 2 - self.current_resolution[0] // 5, self.current_resolution[1] // 2 - 100))
            self.display_button(mouse_x, mouse_y, self.buttons_rects['restart_button_rect'], "MENU")
            self.display_button(mouse_x, mouse_y, self.buttons_rects['quit_button_rect'], "QUIT")

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        paused = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.buttons_rects['restart_button_rect'].collidepoint(mouse_x, mouse_y):
                        self.reset_game()
                        paused = False

                    elif self.buttons_rects['quit_button_rect'].collidepoint(mouse_x, mouse_y):
                        self.close_game()

            pygame.draw.circle(self.screen, (255, 0, 0), (mouse_x, mouse_y), 5)
            pygame.display.flip()
            self.clock.tick(60)


class Fruit:
    images = {}

    def __init__(self, name, speed):
        self.name = name
        self._x_pos = random.randint(100, 1300)
        self._y_pos = 800
        self.speed = speed
        if name not in Fruit.images:
            img_path = os.path.join('fruits', name + '.png')
            img = pygame.image.load(img_path).convert_alpha()
            Fruit.images[name] = pygame.transform.scale(img, (100, 100))
        self.img = Fruit.images[name]
        self.img_pos = [self._x_pos, self._y_pos]

    @property
    def x_pos(self):
        return self._x_pos

    @property
    def y_pos(self):
        return self._y_pos

    @x_pos.setter
    def x_pos(self, value):
        self._x_pos = value

    @y_pos.setter
    def y_pos(self, value):
        self._y_pos = value

    @property
    def img_pos(self):
        return self._img_pos

    @img_pos.setter
    def img_pos(self, pos_x_y):
        self._img_pos = pos_x_y


def test_game():
    game = Game()
    game.run_game()


test_game()
