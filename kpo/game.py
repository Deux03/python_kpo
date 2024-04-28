import pygame
import sys
import os
import random


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Fruit Ninja")
        self.screen = pygame.display.set_mode((1400, 800))
        self.clock = pygame.time.Clock()
        self.fruits = []
        self.fruit_types = ['watermelon', 'apple', 'banana']
        self.speed_increase_interval = 5000  # 5 másodpercenként növeljük a sebességet
        self.last_speed_increase_time = pygame.time.get_ticks()
        self.fruit_speed = -1
        self.font = pygame.font.Font('fonts/comic.ttf', 30)
        self.score = 0
        self.lives = 3
        self.game_over = False
        self.end_time = None
        self.restart_button_rect = pygame.Rect(600, 500, 200, 50)
        self.start_button_rect = pygame.Rect(600, 350, 200, 50)
        self.game_started = False
        self.start_ticks = None

    def reset_game(self):
        self.last_speed_increase_time = pygame.time.get_ticks()
        self.fruit_speed = -1
        self.score = 0
        self.lives = 3
        self.game_over = False
        self.end_time = None
        self.game_started = False
        self.fruits = []



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

    def display_u_lost(self):
        u_lost_text = self.font.render(f'YOU LOST!', True, (255, 0, 0))
        self.screen.blit(u_lost_text, (600, 300))
        total_score = self.font.render(f'Total score: {self.score}', True, (255, 0, 0))
        self.screen.blit(total_score, (600, 340))
        timer_text = self.font.render(f'Time: {self.end_time:.2f}s', True, (255, 0, 0))
        self.screen.blit(timer_text, (600, 380))

    def display_restart_button(self, mouse_x, mouse_y):
        hover = self.restart_button_rect.collidepoint(mouse_x, mouse_y)
        button_color = (0, 200, 0) if hover else (255, 0, 0)

        pygame.draw.rect(self.screen, button_color, self.restart_button_rect)
        button_text = self.font.render('Restart Game', True, (255, 255, 255))
        text_rect = button_text.get_rect(center=self.restart_button_rect.center)
        self.screen.blit(button_text, text_rect)

    def display_start_button(self, mouse_x, mouse_y):
        hover = self.start_button_rect.collidepoint(mouse_x, mouse_y)
        button_color = (0, 200, 0) if hover else (255, 0, 0)
        pygame.draw.rect(self.screen, button_color, self.start_button_rect)
        button_text = self.font.render('Start Game', True, (255, 255, 255))
        text_rect = button_text.get_rect(center=self.start_button_rect.center)
        self.screen.blit(button_text, text_rect)

    def speed_increaser(self, current_time):
        if current_time - self.last_speed_increase_time > self.speed_increase_interval:
            self.fruit_speed -= 1.2
            self.last_speed_increase_time = current_time

    def fruits_movement(self, mouse_x, mouse_y):
        for fruit in self.fruits[:]:
            fruit.y_pos += self.fruit_speed
            fruit.img_pos = [fruit.x_pos, fruit.y_pos]

            # Gyümölcs befoglaló dobozának kiszámítása
            fruit_rect = pygame.Rect(fruit.x_pos, fruit.y_pos, 100, 100)

            # Ellenőrizzük, hogy az egér a gyümölcs befoglaló dobozán belül van-e
            if fruit_rect.collidepoint(mouse_x, mouse_y):
                self.fruits.remove(fruit)
                self.score += 1
                continue

            self.screen.blit(fruit.img, fruit.img_pos)
            if fruit.y_pos < -100:
                self.fruits.remove(fruit)
                self.lives -= 1

    def spawn_random_fruits(self):
        if random.randint(0, 30) == 0:
            fruit_type = random.choice(self.fruit_types)
            self.fruits.append(Fruit(fruit_type, self.fruit_speed))

    def close_game(self):
        pygame.quit()
        sys.exit()

    def run_game(self):
        pygame.mouse.set_visible(0)

        while True:
            self.screen.fill((0, 0, 0))
            current_ticks = pygame.time.get_ticks()
            mouse_x, mouse_y = pygame.mouse.get_pos()

            if not self.game_started:
                self.display_start_button(mouse_x, mouse_y)

            else:
                if self.lives == 0 and not self.game_over:
                    self.game_over = True
                    self.end_time = (current_ticks - self.start_ticks) / 1000

                if not self.game_over:
                    self.speed_increaser(current_ticks)
                    self.display_timer(current_ticks, self.start_ticks)
                    self.display_score()
                    self.display_lives()
                    self.fruits_movement(mouse_x, mouse_y)
                    self.spawn_random_fruits()
                else:
                    self.display_u_lost()
                    self.display_restart_button(mouse_x, mouse_y)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.close_game()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.restart_button_rect.collidepoint(mouse_x, mouse_y):
                        if self.game_over:
                            self.reset_game()
                    if self.start_button_rect.collidepoint(mouse_x, mouse_y):
                        if not self.game_started:
                            self.game_started = True
                            self.start_ticks = pygame.time.get_ticks()

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
