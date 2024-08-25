import json
import os

import pygame
import sys
import random

from kpo.fruit import Fruit


class Game:
    def __init__(self, res_x=1400, res_y=800):
        """
        Initialize the game with the given resolution.

        This method sets up the initial state of the game, including screen resolution, assets loading,
        and initializing Pygame modules.

        :param res_x: The width of the game window. Default is 1400.
        :type res_x: int
        :param res_y: The height of the game window. Default is 800.
        :type res_y: int
        """
        self.setting_buttons_rects = None
        self.buttons_rects = None
        self.background_img = None
        self.start_bg_img = None
        self.ig_background_image = None
        pygame.init()
        pygame.mixer.init()
        pygame.display.set_caption("Fruit Ninja")
        self.current_resolution = (res_x, res_y)
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
        self.pause_start_ticks = 0
        self.total_pause_duration = 0
        self.state = "menu"

        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        font_path = os.path.join(self.base_dir, 'fonts', 'comic.ttf')
        slash_sound_path = os.path.join(self.base_dir, 'sounds', 'slash.mp3')
        losing_life_sound_path = os.path.join(self.base_dir, 'sounds', 'losing_life.mp3')

        self.font = self.load_font(font_path, 30)
        self.load_images(self.base_dir)
        self.calculate_button_positions()
        self.best_scores = {}
        self.load_best_scores()
        self.blink_active = False
        self.blink_start_time = 0
        self.blink_duration = 200
        self.slash_sound = self.load_sound(slash_sound_path)
        if self.slash_sound:
            self.slash_sound.set_volume(0.25)
        self.losing_life_sound = self.load_sound(losing_life_sound_path)
        if self.losing_life_sound:
            self.losing_life_sound.set_volume(0.4)
        self.end_scr_txt = "YOU LOST"
        self.record_scr_id = 1

    def load_font(self, font_path, size):
        """
               Load a font from the specified path and size.

               :param font_path: The path to the font file.
               :type font_path: str
               :param size: The size of the font to load.
               :type size: int
               :return: A Pygame font object. If the specified font cannot be loaded, returns a default font.
               :rtype: pygame.font.Font
        """
        try:
            return pygame.font.Font(font_path, size)
        except FileNotFoundError:
            return pygame.font.Font(None, size)

    def load_sound(self, sound_path):
        """
        Load a sound effect from the specified path.

        :param sound_path: The path to the sound file.
        :type sound_path: str
        :return: A Pygame Sound object if the file is found; otherwise, None.
        :rtype: pygame.mixer.Sound or None
        """
        try:
            return pygame.mixer.Sound(sound_path)
        except FileNotFoundError:
            return None

    def load_images(self, base_dir):
        """
        Load background images and scale them to fit the game window.

        This method loads the images for the game background and the welcome screen,
        and scales them to the current screen resolution.

        :param base_dir: The base directory where the images are located.
        :type base_dir: str
        """
        background_path = os.path.join(base_dir, 'background', 'background.jpg')
        welcome_screen_path = os.path.join(base_dir, 'background', 'WelcomeScreen.jpg')
        self.ig_background_image = self.load_and_scale_image(background_path, self.current_resolution)
        self.start_bg_img = self.load_and_scale_image(welcome_screen_path, self.current_resolution)
        self.background_img = self.start_bg_img

    def load_and_scale_image(self, filepath, size):
        """
               Load an image from a file and scale it to the specified size.

               :param filepath: The path to the image file.
               :type filepath: str
               :param size: The size to scale the image to (width, height).
               :type size: tuple
               :return: A Pygame Surface object containing the scaled image. If the file is not found, returns a blank Surface.
               :rtype: pygame.Surface
               """
        try:
            image = pygame.image.load(filepath).convert()
            return pygame.transform.scale(image, size)
        except FileNotFoundError:
            return pygame.Surface(size)

    def calculate_button_positions(self):
        """
                Calculate the positions of the menu and settings buttons based on the current resolution.

                This method sets up the button rectangles for the game menu, restart, quit, and settings.
                """
        mid_x = self.current_resolution[0] // 2
        mid_y = self.current_resolution[1] // 2
        self.buttons_rects = {
            'restart_button_rect': pygame.Rect(mid_x - 100, mid_y + 100, 200, 50),
            'start_button_rect': pygame.Rect(mid_x - 100, mid_y, 200, 50),
            'settings_button_rect': pygame.Rect(mid_x - 100, mid_y + 100, 200, 50),
            'quit_button_rect': pygame.Rect(mid_x - 100, mid_y + 200, 200, 50),
            'back_button_rect': pygame.Rect(mid_x - 100, self.current_resolution[1] - 100, 300, 50)
        }
        self.setting_buttons_rects = {
            'res_1280x720': pygame.Rect(mid_x - 100, mid_y + 100, 300, 50),
            'res_1400x800': pygame.Rect(mid_x - 100, mid_y, 300, 50),
            'res_1920x1080': pygame.Rect(mid_x - 100, mid_y - 100, 300, 50)
        }

    def reset_game(self):
        """
                Reset the game state to its initial settings.

                This method resets scores, lives, speed, and game state, effectively restarting the game.
                """
        self.last_speed_increase_time = pygame.time.get_ticks()
        self.fruit_speed = -1
        self.score = 0
        self.lives = 3
        self.game_over = False
        self.end_time = None
        self.game_started = False
        self.fruits = []
        self.background_img = self.start_bg_img
        self.total_pause_duration = 0

    def display_pause(self):
        """
                Display a pause message on the screen.

                This method renders and displays a text message indicating the game is paused.
                """
        pause_text = self.font.render(f'P - pause', True, (255, 255, 255))
        self.screen.blit(pause_text, (self.current_resolution[0] - 150, 10))

    def display_timer(self, current_time, start_time, dest_x=10, dest_y=10, color=(255, 255, 255)):
        """
                Display the elapsed game time on the screen.

                :param current_time: The current time in milliseconds.
                :type current_time: int
                :param start_time: The game start time in milliseconds.
                :type start_time: int
                :param dest_x: The x-coordinate on the screen to display the timer. Default is 10.
                :type dest_x: int
                :param dest_y: The y-coordinate on the screen to display the timer. Default is 10.
                :type dest_y: int
                :param color: The color of the timer text. Default is white (255, 255, 255).
                :type color: tuple
                """
        elapsed_time = (current_time - start_time - self.total_pause_duration) / 1000
        timer_text = self.font.render(f'Time: {elapsed_time:.2f}s', True, color)
        self.screen.blit(timer_text, (dest_x, dest_y))

    def display_score(self):
        """
               Display the current score on the screen.
               """
        score_text = self.font.render(f'Score: {self.score}', True, (255, 255, 255))
        self.screen.blit(score_text, (10, 50))

    def display_lives(self):
        """
                Display the number of remaining lives on the screen.
                """
        lives_text = self.font.render(f'Lives: {self.lives}', True, (255, 255, 255))
        self.screen.blit(lives_text, (10, 90))

    def display_fps(self):
        """
                Display the current frames per second (FPS) on the screen.
                """
        fps_text = self.font.render(f'FPS: {self.clock.get_fps():.0f}', True, (255, 255, 255))
        self.screen.blit(fps_text, (10, 130))

    def display_game_over(self, mouse_x, mouse_y):
        """
                Display the game over screen and options for restarting or quitting.

                :param mouse_x: The x-coordinate of the mouse position.
                :type mouse_x: int
                :param mouse_y: The y-coordinate of the mouse position.
                :type mouse_y: int
                """
        self.screen.blit(self.background_img, (0, 0))

        self.display_best_scores()

        u_lost_text = self.font.render(self.end_scr_txt, True, (255, 0, 0))
        self.screen.blit(u_lost_text, (self.current_resolution[0] // 2 - 100, self.current_resolution[1] // 2 - 100))
        total_score = self.font.render(f'Total score: {self.score}', True, (255, 0, 0))
        self.screen.blit(total_score, (self.current_resolution[0] // 2 - 100, self.current_resolution[1] // 2 - 50))
        timer_text = self.font.render(f'Time: {self.end_time:.2f}s', True, (255, 0, 0))
        self.screen.blit(timer_text, (self.current_resolution[0] // 2 - 100, self.current_resolution[1] // 2))

        self.display_button(mouse_x, mouse_y, self.buttons_rects['restart_button_rect'], "MENU")
        self.display_button(mouse_x, mouse_y, self.buttons_rects['quit_button_rect'], "QUIT")

    def display_button(self, mouse_x, mouse_y, btn_rect, text):
        """
                Display a button with hover effects and text.

                :param mouse_x: The x-coordinate of the mouse position.
                :type mouse_x: int
                :param mouse_y: The y-coordinate of the mouse position.
                :type mouse_y: int
                :param btn_rect: The rectangle defining the button's position and size.
                :type btn_rect: pygame.Rect
                :param text: The text to display on the button.
                :type text: str
                """
        hover = btn_rect.collidepoint(mouse_x, mouse_y)
        button_color = (0, 200, 0) if hover else (255, 0, 0)
        pygame.draw.rect(self.screen, button_color, btn_rect)
        button_text = self.font.render(text, True, (255, 255, 255))
        text_rect = button_text.get_rect(center=btn_rect.center)
        self.screen.blit(button_text, text_rect)

    def speed_increaser(self, current_time):
        """
                Increase the speed of falling fruits over time.

                This method checks if enough time has passed to increase the fruit falling speed.

                :param current_time: The current time in milliseconds.
                :type current_time: int
                """
        if current_time - self.last_speed_increase_time > self.speed_increase_interval:
            self.fruit_speed -= 1.05
            self.last_speed_increase_time = current_time

    def fruits_movement(self, mouse_x, mouse_y):
        """
               Handle the movement of fruits and detect interactions with the mouse.

               This method moves fruits downward, checks for collisions with the mouse cursor (slicing),
               and removes fruits that fall off the screen.

               :param mouse_x: The x-coordinate of the mouse position.
               :type mouse_x: int
               :param mouse_y: The y-coordinate of the mouse position.
               :type mouse_y: int
               """
        for fruit in self.fruits[:]:
            fruit.y_pos += self.fruit_speed
            fruit.img_pos = [fruit.x_pos, fruit.y_pos]

            fruit_rect = pygame.Rect(fruit.x_pos, fruit.y_pos, 100, 100)

            if fruit_rect.collidepoint(mouse_x, mouse_y):
                self.fruits.remove(fruit)
                self.score += 1
                if self.slash_sound:
                    self.slash_sound.play()
                continue

            self.screen.blit(fruit.img, fruit.img_pos)
            if fruit.y_pos < -100:
                self.fruits.remove(fruit)
                self.lives -= 1
                if self.losing_life_sound:
                    self.losing_life_sound.play()
                # Activate the blink effect when a life is lost
                self.blink_active = True
                self.blink_start_time = pygame.time.get_ticks()

    def spawn_random_fruits(self):
        """
                Spawn random fruits at random positions.

                This method randomly decides when to spawn a fruit and adds it to the game.
                """
        if random.randint(0, 40) == 0:
            fruit_type = random.choice(self.fruit_types)
            self.fruits.append(Fruit(fruit_type, self.fruit_speed, self.current_resolution))

    def close_game(self):
        """
                Close the game and exit the program.
                """
        pygame.quit()
        sys.exit()

    def run_game(self):
        """
                Run the main game loop.

                This method contains the main game loop that handles game states, user input,
                and updates the game screen.
                """
        pygame.mouse.set_visible(0)

        while True:
            self.screen.blit(self.background_img, (0, 0))
            current_ticks = pygame.time.get_ticks()
            mouse_x, mouse_y = pygame.mouse.get_pos()

            if self.state == "menu":
                self.display_button(mouse_x, mouse_y, self.buttons_rects['start_button_rect'], "START")
                self.display_button(mouse_x, mouse_y, self.buttons_rects['settings_button_rect'], "SETTINGS")
                self.display_button(mouse_x, mouse_y, self.buttons_rects['quit_button_rect'], "QUIT")
            elif self.state == "game":
                if self.lives <= 0 and not self.game_over:
                    self.game_over = True
                    self.end_time = (current_ticks - self.start_ticks - self.total_pause_duration) / 1000
                    if self.update_best_scores():
                        self.save_new_best_scores()
                        self.end_scr_txt = f"{self.record_scr_id}. NEW RECORD SCORE: "
                    else:
                        self.end_scr_txt = "YOU LOST"

                if not self.game_over:
                    self.speed_increaser(current_ticks)
                    self.display_timer(current_ticks, self.start_ticks)
                    self.display_score()
                    self.display_lives()
                    self.display_fps()
                    self.display_pause()
                    self.fruits_movement(mouse_x, mouse_y)
                    self.spawn_random_fruits()
                    self.activate_blink_if_lost_life(current_ticks)
                else:
                    self.display_game_over(mouse_x, mouse_y)
            elif self.state == "settings":
                for name, rect in self.setting_buttons_rects.items():
                    text = name.replace('_', ': ')
                    self.display_button(mouse_x, mouse_y, rect, text)
                self.display_button(mouse_x, mouse_y, self.buttons_rects['back_button_rect'], "BACK")
            elif self.state == "pause":
                pause_text = self.font.render("Game paused, press 'P' to unpause", True, (255, 255, 255))
                self.screen.blit(pause_text, (
                    self.current_resolution[0] // 2 - self.current_resolution[0] // 5,
                    self.current_resolution[1] // 2 - 100))
                self.display_button(mouse_x, mouse_y, self.buttons_rects['restart_button_rect'], "MENU")
                self.display_button(mouse_x, mouse_y, self.buttons_rects['quit_button_rect'], "QUIT")

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.close_game()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.state == "menu":
                        if self.buttons_rects['start_button_rect'].collidepoint(mouse_x, mouse_y):
                            self.game_started = True
                            self.start_ticks = pygame.time.get_ticks()
                            self.background_img = self.ig_background_image
                            self.state = "game"
                        elif self.buttons_rects['settings_button_rect'].collidepoint(mouse_x, mouse_y):
                            self.state = "settings"
                        elif self.buttons_rects['quit_button_rect'].collidepoint(mouse_x, mouse_y):
                            self.close_game()
                    elif self.state == "game" and self.game_over:
                        if self.buttons_rects['restart_button_rect'].collidepoint(mouse_x, mouse_y):
                            self.reset_game()
                            self.state = "menu"
                        elif self.buttons_rects['quit_button_rect'].collidepoint(mouse_x, mouse_y):
                            self.close_game()
                    elif self.state == "settings":
                        if self.buttons_rects['back_button_rect'].collidepoint(mouse_x, mouse_y):
                            self.state = "menu"
                        else:
                            for name in self.setting_buttons_rects.keys():
                                if self.setting_buttons_rects[name].collidepoint(mouse_x, mouse_y):
                                    res = name[4::].split('x')
                                    self.update_resolution(res)
                    elif self.state == "pause":
                        if self.buttons_rects['restart_button_rect'].collidepoint(mouse_x, mouse_y):
                            self.reset_game()
                            self.state = "menu"
                        elif self.buttons_rects['quit_button_rect'].collidepoint(mouse_x, mouse_y):
                            self.close_game()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p and self.state == "game":
                        self.pause_start_ticks = pygame.time.get_ticks()
                        self.state = "pause"
                    elif event.key == pygame.K_p and self.state == "pause":
                        self.total_pause_duration += pygame.time.get_ticks() - self.pause_start_ticks
                        self.state = "game"

            pygame.draw.circle(self.screen, (255, 0, 0), (mouse_x, mouse_y), 5)
            pygame.display.flip()
            self.clock.tick(60)

    def update_resolution(self, res):
        """
               Update the game resolution and adjust related elements.

               :param res: A tuple containing the new resolution (width, height).
               :type res: tuple
               """
        self.current_resolution = (int(res[0]), int(res[1]))
        self.screen = pygame.display.set_mode(self.current_resolution)
        self.calculate_button_positions()
        self.load_images(self.base_dir)

    def load_best_scores(self):
        """
                Load the best scores from a JSON file.

                If the file is not found, it initializes the best scores with default values.
                """
        try:
            with open('best_scores.json', 'r') as file:
                self.best_scores = json.load(file)


        except FileNotFoundError:
            scores = {
                "1": [0, 0],
                "2": [0, 0],
                "3": [0, 0],
                "4": [0, 0],
                "5": [0, 0]
            }
            with open('best_scores.json', 'w') as file:
                json.dump(scores, file, indent=4)
                self.best_scores = scores

    def update_best_scores(self):
        """
        Updates the list of best scores by inserting the current score into the appropriate position, if applicable.

        This method checks if the current game score (`self.score`) and time (`self.end_time`) qualify to be included
        in the list of best scores. If the current score is higher than any of the existing best scores, or if it matches
        an existing score but was achieved in a shorter time, it will be inserted into the best scores list. The lower
        scores will be shifted down one rank, and the lowest score will be removed if necessary to maintain only the top 5 scores.

        The `best_scores` attribute is updated, where each entry represents a rank and contains a list with two elements:
        the score and the time taken to achieve that score.

        Example:
            If the current score is 300 and this score is higher than the 3rd best score (or is the same but achieved in less time),
            then this method will insert the current score into the 3rd position and shift the existing 3rd to 5th scores down one rank.

        :return: True if the best scores were updated, False otherwise.
        :rtype: bool
        """
        update_happened = False
        current_score = self.score
        current_time = self.end_time

        # Convert the best_scores dictionary to a list of tuples for easier manipulation
        best_scores_list = [(key, int(value[0]), float(value[1])) for key, value in self.best_scores.items()]

        # Sort the list based on the scores, highest score first. If scores are the same, sort by time (ascending).
        best_scores_list.sort(key=lambda x: (-x[1], x[2]))

        for i, (key, best_score, best_time) in enumerate(best_scores_list):
            if current_score > best_score or (current_score == best_score and current_time < best_time):
                self.record_scr_id = key
                # Shift lower scores down
                for j in range(len(best_scores_list) - 1, i, -1):
                    best_scores_list[j] = best_scores_list[j - 1]

                # Insert the new score
                best_scores_list[i] = (key, current_score, current_time)
                update_happened = True
                break

        if update_happened:
            # Convert back to the original dictionary format
            for i, (key, score, time) in enumerate(best_scores_list):
                self.best_scores[str(i + 1)] = [score, time]

        return update_happened

    def save_new_best_scores(self):
        """
        The method saves the current best scores into the 'best_scores.json' file.
        """
        with open('best_scores.json', 'w') as file:
            json.dump(self.best_scores, file, indent=4)

    def display_best_scores(self):
        """
                Display the list of best scores on the screen.
                """
        title_text = self.font.render('Best Scores:', True, (255, 255, 0))
        start_y = self.current_resolution[1] // 2 - 300
        self.screen.blit(title_text, (self.current_resolution[0] // 2 - 100, start_y))

        for i, (rank, (score, time)) in enumerate(sorted(self.best_scores.items(), key=lambda x: int(x[0]))):
            score_text = self.font.render(f'{rank}: Score: {score}, Time: {time:.2f}s', True, (255, 255, 255))
            self.screen.blit(score_text, (self.current_resolution[0] // 2 - 100, start_y + 30 + i * 30))

    def activate_blink_if_lost_life(self, current_ticks):
        """
                Activate a red blink effect on the screen when a life is lost.

                :param current_ticks: The current time in milliseconds.
                :type current_ticks: int
                """
        if self.blink_active:
            if current_ticks - self.blink_start_time <= self.blink_duration:
                red_overlay = pygame.Surface(self.current_resolution)
                red_overlay.set_alpha(128)
                red_overlay.fill((255, 0, 0))
                self.screen.blit(red_overlay, (0, 0))
            else:
                self.blink_active = False


def main():
    game = Game()
    game.run_game()


if __name__ == "__main__":
    main()
