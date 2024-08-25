import unittest
from unittest.mock import patch, MagicMock, mock_open
import pygame
import os
from kpo.game import Game

class TestGame(unittest.TestCase):

    def setUp(self):
        # Set up patchers for Pygame methods
        self.patcher_init = patch('pygame.init')
        self.patcher_mixer_init = patch('pygame.mixer.init')
        self.patcher_set_caption = patch('pygame.display.set_caption')
        self.patcher_set_mode = patch('pygame.display.set_mode', return_value=MagicMock())

        # Use specific mocks for each sound
        self.mock_slash_sound = MagicMock()
        self.mock_losing_life_sound = MagicMock()

        # Mock Sound call with side effect to return different mocks based on the sound file
        self.patcher_sound = patch('pygame.mixer.Sound', side_effect=lambda path: self.mock_slash_sound if 'slash.mp3' in path else self.mock_losing_life_sound)

        # Create a mock surface to return when loading images
        self.mock_surface = MagicMock()
        self.mock_surface.convert.return_value = self.mock_surface  # Mock convert() method
        self.mock_surface.convert_alpha.return_value = self.mock_surface  # Mock convert_alpha() method if needed

        self.patcher_image_load = patch('pygame.image.load', return_value=self.mock_surface)
        self.patcher_transform_scale = patch('pygame.transform.scale', return_value=self.mock_surface)

        # Mock get_ticks to return a consistent value
        self.patcher_get_ticks = patch('pygame.time.get_ticks', return_value=1000)

        # Setup the mock font to handle FileNotFoundError correctly
        self.mock_font_instance = MagicMock()
        self.patcher_font = patch('pygame.font.Font', return_value=self.mock_font_instance)

        # Start patchers
        self.mock_init = self.patcher_init.start()
        self.mock_mixer_init = self.patcher_mixer_init.start()
        self.mock_set_caption = self.patcher_set_caption.start()
        self.mock_set_mode = self.patcher_set_mode.start()
        self.mock_font = self.patcher_font.start()
        self.mock_sound = self.patcher_sound.start()
        self.mock_image_load = self.patcher_image_load.start()
        self.mock_transform_scale = self.patcher_transform_scale.start()
        self.mock_get_ticks = self.patcher_get_ticks.start()

        self.game = Game()
        self.game.current_resolution = (1400, 800)
        self.game.fruit_speed = -1
        self.game.fruit_types = ['watermelon', 'apple', 'banana']

        # Reset score and end_time for specific tests
        self.game.score = 0
        self.game.end_time = None

        # Set initial best_scores to a known state for testing
        self.game.best_scores = {
            '1': [0, 0],
            '2': [0, 0],
            '3': [0, 0],
            '4': [0, 0],
            '5': [0, 0]
        }

    def tearDown(self):
        patch.stopall()

    def test_init(self):
        self.mock_init.assert_called_once()
        self.mock_mixer_init.assert_called_once()
        self.mock_set_caption.assert_called_with("Fruit Ninja")
        self.mock_set_mode.assert_called_with((1400, 800))

        self.assertEqual(self.game.current_resolution, (1400, 800))
        self.assertEqual(self.game.screen, self.mock_set_mode.return_value)
        self.assertIsInstance(self.game.clock, pygame.time.Clock)

        self.assertEqual(self.game.score, 0)
        self.assertEqual(self.game.lives, 3)
        self.assertFalse(self.game.game_over)
        self.assertIsNone(self.game.end_time)
        self.assertFalse(self.game.game_started)
        self.assertIsNone(self.game.start_ticks)
        self.assertEqual(self.game.pause_start_ticks, 0)
        self.assertEqual(self.game.total_pause_duration, 0)
        self.assertEqual(self.game.state, "menu")

        game_base_dir = os.path.dirname(os.path.abspath(self.game.__module__.replace('.', os.sep) + '.py'))
        self.assertEqual(self.game.base_dir, game_base_dir)

        font_path = os.path.join(game_base_dir, 'fonts', 'comic.ttf')
        self.mock_font.assert_called_with(font_path, 30)
        self.assertEqual(self.game.font, self.mock_font_instance)  # Use the specific mock instance

        slash_sound_path = os.path.join(game_base_dir, 'sounds', 'slash.mp3')
        losing_life_sound_path = os.path.join(game_base_dir, 'sounds', 'losing_life.mp3')
        self.mock_sound.assert_any_call(slash_sound_path)
        self.mock_sound.assert_any_call(losing_life_sound_path)

        self.assertIsNotNone(self.game.slash_sound)
        self.mock_slash_sound.set_volume.assert_called_with(0.25)

        self.assertIsNotNone(self.game.losing_life_sound)
        self.mock_losing_life_sound.set_volume.assert_called_with(0.4)

        self.assertEqual(self.game.last_speed_increase_time, 1000)

        self.assertEqual(self.game.fruit_types, ['watermelon', 'apple', 'banana'])
        self.assertEqual(self.game.fruit_speed, -1)
        self.assertEqual(self.game.speed_increase_interval, 5000)
        self.assertEqual(self.game.fruits, [])

        expected_best_scores = {
            '1': [0, 0],
            '2': [0, 0],
            '3': [0, 0],
            '4': [0, 0],
            '5': [0, 0]
        }
        self.assertEqual(self.game.best_scores, expected_best_scores)

        self.assertFalse(self.game.blink_active)
        self.assertEqual(self.game.blink_start_time, 0)
        self.assertEqual(self.game.blink_duration, 200)
        self.assertEqual(self.game.end_scr_txt, "YOU LOST")
        self.assertEqual(self.game.record_scr_id, 1)

        self.assertIsNotNone(self.game.start_bg_img)
        self.assertIsNotNone(self.game.ig_background_image)
        self.assertEqual(self.game.background_img, self.game.start_bg_img)

        self.assertIsNotNone(self.game.buttons_rects)
        self.assertIsNotNone(self.game.setting_buttons_rects)

    def test_load_font(self):
        # Testing load_font method with a valid path
        font_path = os.path.join(self.game.base_dir, 'fonts', 'comic.ttf')
        font = self.game.load_font(font_path, 30)
        self.mock_font.assert_called_with(font_path, 30)
        self.assertIs(font, self.mock_font_instance)  # Use assertIs to check for the same mock instance

        # Testing load_font method with an invalid path
        with patch('pygame.font.Font', side_effect=[FileNotFoundError, self.mock_font_instance]) as mock_font:
            font = self.game.load_font('invalid_path', 30)
            mock_font.assert_called_with(None, 30)  # Should fall back to default font
            self.assertIsNotNone(font)

    def test_load_sound(self):
        # Testing load_sound method with a valid path
        sound_path = os.path.join(self.game.base_dir, 'sounds', 'slash.mp3')
        sound = self.game.load_sound(sound_path)
        self.mock_sound.assert_called_with(sound_path)
        self.assertEqual(sound, self.mock_slash_sound)

        # Testing load_sound method with an invalid path
        with patch('pygame.mixer.Sound', side_effect=FileNotFoundError):
            sound = self.game.load_sound('invalid_path')
            self.assertIsNone(sound)  # Should return None if the sound file is not found

    def test_load_images(self):
        # Testing load_images method to check if images are loaded and scaled correctly
        self.game.load_images(self.game.base_dir)
        background_path = os.path.join(self.game.base_dir, 'background', 'background.jpg')
        welcome_screen_path = os.path.join(self.game.base_dir, 'background', 'WelcomeScreen.jpg')
        self.mock_image_load.assert_any_call(background_path)
        self.mock_image_load.assert_any_call(welcome_screen_path)
        self.mock_transform_scale.assert_any_call(self.mock_surface, self.game.current_resolution)
        self.assertEqual(self.game.ig_background_image, self.mock_surface)
        self.assertEqual(self.game.start_bg_img, self.mock_surface)
        self.assertEqual(self.game.background_img, self.game.start_bg_img)

    def test_load_and_scale_image(self):
        # Testing load_and_scale_image method with a valid path
        filepath = os.path.join(self.game.base_dir, 'background', 'background.jpg')
        image = self.game.load_and_scale_image(filepath, self.game.current_resolution)
        self.mock_image_load.assert_called_with(filepath)
        self.mock_transform_scale.assert_called_with(self.mock_surface, self.game.current_resolution)
        self.assertEqual(image, self.mock_surface)

        # Testing load_and_scale_image method with an invalid path
        with patch('pygame.image.load', side_effect=FileNotFoundError):
            image = self.game.load_and_scale_image('invalid_path', self.game.current_resolution)
            self.assertIsNotNone(image)
            self.assertNotEqual(image, self.mock_surface)

    def test_calculate_button_positions(self):
        # Test calculate_button_positions method
        self.game.calculate_button_positions()
        mid_x = self.game.current_resolution[0] // 2
        mid_y = self.game.current_resolution[1] // 2
        expected_buttons_rects = {
            'restart_button_rect': pygame.Rect(mid_x - 100, mid_y + 100, 200, 50),
            'start_button_rect': pygame.Rect(mid_x - 100, mid_y, 200, 50),
            'settings_button_rect': pygame.Rect(mid_x - 100, mid_y + 100, 200, 50),
            'quit_button_rect': pygame.Rect(mid_x - 100, mid_y + 200, 200, 50),
            'back_button_rect': pygame.Rect(mid_x - 100, self.game.current_resolution[1] - 100, 300, 50)
        }
        expected_setting_buttons_rects = {
            'res_1280x720': pygame.Rect(mid_x - 100, mid_y + 100, 300, 50),
            'res_1400x800': pygame.Rect(mid_x - 100, mid_y, 300, 50),
            'res_1920x1080': pygame.Rect(mid_x - 100, mid_y - 100, 300, 50)
        }
        self.assertEqual(self.game.buttons_rects, expected_buttons_rects)
        self.assertEqual(self.game.setting_buttons_rects, expected_setting_buttons_rects)

    def test_speed_increaser(self):
        # Test speed_increaser method
        self.game.last_speed_increase_time = 0
        self.game.speed_increase_interval = 5000
        self.game.fruit_speed = -5

        current_time = 6000
        self.game.speed_increaser(current_time)

        self.assertEqual(self.game.fruit_speed, -6.05)
        self.assertEqual(self.game.last_speed_increase_time, 6000)

    @patch('random.randint', return_value=0)  # Mock random.randint to always return 0 to spawn a fruit
    @patch('random.choice', return_value='apple')  # Mock random.choice to always choose 'apple'
    def test_spawn_random_fruits(self, mock_randint, mock_choice):
        self.game.fruits = []  # Ensure fruits list is empty before test
        self.game.spawn_random_fruits()

        self.assertEqual(len(self.game.fruits), 1)
        fruit = self.game.fruits[0]
        # Use the actual attributes from the Fruit class
        self.assertEqual(fruit.name, 'apple')  # Correct attribute name from Fruit class
        self.assertEqual(fruit.speed, self.game.fruit_speed)
        self.assertEqual(fruit.img_pos, [fruit.x_pos, fruit.y_pos])

    @patch('pygame.display.set_mode', return_value=MagicMock())
    def test_update_resolution(self, mock_set_mode):
        # Test update_resolution method
        new_resolution = (1920, 1080)
        self.game.update_resolution(new_resolution)

        self.assertEqual(self.game.current_resolution, new_resolution)
        mock_set_mode.assert_called_with(new_resolution)
        self.assertEqual(self.game.screen, mock_set_mode.return_value)

        mid_x = new_resolution[0] // 2
        mid_y = new_resolution[1] // 2
        expected_buttons_rects = {
            'restart_button_rect': pygame.Rect(mid_x - 100, mid_y + 100, 200, 50),
            'start_button_rect': pygame.Rect(mid_x - 100, mid_y, 200, 50),
            'settings_button_rect': pygame.Rect(mid_x - 100, mid_y + 100, 200, 50),
            'quit_button_rect': pygame.Rect(mid_x - 100, mid_y + 200, 200, 50),
            'back_button_rect': pygame.Rect(mid_x - 100, new_resolution[1] - 100, 300, 50)
        }
        self.assertEqual(self.game.buttons_rects, expected_buttons_rects)

    @patch('builtins.open', new_callable=mock_open)
    @patch('json.dump')
    def test_save_new_best_scores(self, mock_json_dump, mock_open):
        # Test save_new_best_scores method
        self.game.save_new_best_scores()
        mock_open.assert_called_with('best_scores.json', 'w')
        mock_json_dump.assert_called_with(self.game.best_scores, mock_open(), indent=4)

    def test_update_best_scores(self):
        # Set up a realistic starting best_scores for testing
        self.game.best_scores = {
            '1': [300, 50.0],
            '2': [250, 55.0],
            '3': [200, 60.0],
            '4': [150, 65.0],
            '5': [100, 70.0]
        }
        # Set score and time to test best scores update
        self.game.score = 350
        self.game.end_time = 45.0
        # Test update_best_scores method
        self.game.update_best_scores()

        expected_best_scores = {
            '1': [350, 45.0],  # New high score
            '2': [300, 50.0],
            '3': [250, 55.0],
            '4': [200, 60.0],
            '5': [150, 65.0]
        }
        self.assertEqual(self.game.best_scores, expected_best_scores)

def main():
    unittest.main()

if __name__ == '__main__':
    main()
