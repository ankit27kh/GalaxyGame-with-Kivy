from kivy.config import Config

Config.set('graphics', 'width', '900')
Config.set('graphics', 'height', '400')
from kivy.metrics import dp
from kivy.core.audio import SoundLoader
from kivy.lang import Builder
from kivy.uix.relativelayout import RelativeLayout
from kivy.core.window import Window
from kivy.app import App
from kivy.graphics import Color, Line, Quad, Triangle
from kivy.properties import NumericProperty, Clock, ObjectProperty, StringProperty
from kivy.uix.widget import Widget
from kivy import platform
import random
import time

Builder.load_file('menu.kv')


class MainWidget(RelativeLayout):
    from transforms import transform, transform_perspective, transform_2D
    from user_actions import keyboard_closed, on_keyboard_down, on_keyboard_up, on_touch_down, on_touch_up

    menu_widget = ObjectProperty()
    perspective_point_x = NumericProperty(0)
    perspective_point_y = NumericProperty(0)
    score_txt = StringProperty("Score: 0")

    num_vertical_lines = 8
    vertical_line_spacing = .2
    vertical_lines = []



    num_horizontal_lines = 15
    horizontal_line_spacing = .1
    horizontal_lines = []

    current_offset_y = 0
    refresh_rate = 120
    speed_y = 4
    speed_x = 20
    current_offset_x = 0
    go_left = False
    go_right = False

    num_tiles = 20
    tiles_coordinates = []
    tiles = []

    current_loop_y = 0

    beginning = 10

    ship = None
    ship_coordinates = [(0, 0), (0, 0), (0, 0)]
    ship_width = .1
    ship_height = 0.035
    ship_base = 0.04

    game_start = False
    game_over = False

    menu_title = StringProperty("G    A    L    A    X    Y")
    menu_button = StringProperty("START")

    begin_sound = None
    galaxy_sound = None
    gameover_voice_sound = None
    gameover_impact_sound = None
    music1_sound = None
    restart_sound = None

    vx = .4
    vy = .2

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.init_audio()
        self.init_vertical_lines()
        self.init_horizontal_lines()
        self.init_tiles()
        self.init_ship()
        self.generate_tiles_coordinates()
        self.start_time = time.time()


        if self.is_desktop():
            self._keyboard = Window.request_keyboard(self.keyboard_closed, self)
            self._keyboard.bind(on_key_down=self.on_keyboard_down)
            self._keyboard.bind(on_key_up=self.on_keyboard_up)

        Clock.schedule_interval(self.update, 1 / self.refresh_rate)
        self.galaxy_sound.play()

    def init_audio(self):
        self.begin_sound = SoundLoader.load("RESOURCES_KIVY/2_GALAXY/RESOURCES/audio/begin.wav")
        self.galaxy_sound = SoundLoader.load("RESOURCES_KIVY/2_GALAXY/RESOURCES/audio/galaxy.wav")
        self.gameover_voice_sound = SoundLoader.load("RESOURCES_KIVY/2_GALAXY/RESOURCES/audio/gameover_voice.wav")
        self.gameover_impact_sound = SoundLoader.load("RESOURCES_KIVY/2_GALAXY/RESOURCES/audio/gameover_impact.wav")
        self.music1_sound = SoundLoader.load("RESOURCES_KIVY/2_GALAXY/RESOURCES/audio/music1.wav")
        self.restart_sound = SoundLoader.load("RESOURCES_KIVY/2_GALAXY/RESOURCES/audio/restart.wav")
        self.music1_sound.volume = 1
        self.galaxy_sound.volume = .25
        self.gameover_voice_sound.volume = .6
        self.gameover_impact_sound.volume = .3
        self.restart_sound.volume = .25
        self.begin_sound.volume = .25

    def reset_game(self):
        self.tiles_coordinates = []
        self.current_loop_y = 0
        self.beginning = 10
        self.current_offset_y = 0
        self.current_offset_x = 0
        self.generate_tiles_coordinates()
        self.speed_y = 4
        self.perspective_point_x = self.width / 2
        self.perspective_point_y = self.height * .75
        self.fix_x = self.perspective_point_x
        self.fix_y = self.perspective_point_y
        self.music1_sound.play()
        self.game_over = False
        self.start_time = time.time()

    def is_desktop(self):
        if platform in ('linux', 'win', 'macosx'):
            return True
        else:
            return False

    def init_vertical_lines(self):
        with self.canvas:
            Color(1, 1, 1)
            for i in range(0, self.num_vertical_lines):
                self.vertical_lines.append(Line())

    def init_horizontal_lines(self):
        with self.canvas:
            Color(1, 1, 1)
            for i in range(0, self.num_horizontal_lines):
                self.horizontal_lines.append(Line())

    def init_tiles(self):
        with self.canvas:
            Color(1, 1, 1)
            for i in range(self.num_tiles):
                self.tiles.append(Quad())

    def init_ship(self):
        with self.canvas:
            Color(1, 1, 0)
            self.ship = Triangle()

    def update_ship(self):
        center_x = self.width / 2
        base_y = self.ship_base * self.height
        ship_half_width = self.ship_width * self.width / 2
        ship_height = self.ship_height * self.height

        self.ship_coordinates[0] = (center_x - ship_half_width, base_y)
        self.ship_coordinates[1] = (center_x, ship_height + base_y)
        self.ship_coordinates[2] = (center_x + ship_half_width, base_y)

        x1, y1 = self.transform(*self.ship_coordinates[0])
        x2, y2 = self.transform(*self.ship_coordinates[1])
        x3, y3 = self.transform(*self.ship_coordinates[2])
        self.ship.points = (x1, y1, x2, y2, x3, y3)

    def check_collisions_ship(self):
        for i in range(len(self.tiles_coordinates)):
            ti_x, ti_y = self.tiles_coordinates[i]
            if ti_y > self.current_loop_y + 1:
                return False
            if self.check_collisions_with_tile(ti_x, ti_y):
                return True
        return False

    def check_collisions_with_tile(self, ti_x, ti_y):
        x_min, y_min = self.get_tile_coordinates(ti_x, ti_y)
        x_max, y_max = self.get_tile_coordinates(ti_x + 1, ti_y + 1)

        for i in range(3):
            px, py = self.ship_coordinates[i]
            if x_min <= px <= x_max and y_min <= py <= y_max:
                return True
        return False

    def get_tile_coordinates(self, ti_x, ti_y):
        ti_y = ti_y - self.current_loop_y
        x = self.get_line_x_from_index(ti_x)
        y = self.get_line_y_from_index(ti_y)
        return x, y

    def generate_tiles_coordinates(self):

        last_y = 0
        last_x = 0

        for i in range(len(self.tiles_coordinates) - 1, -1, -1):
            if self.tiles_coordinates[i][1] < self.current_loop_y:
                del self.tiles_coordinates[i]

        if len(self.tiles_coordinates) > 0:
            last_coordinates = self.tiles_coordinates[-1]
            last_y = last_coordinates[1] + 1
            last_x = last_coordinates[0]

        for i in range(len(self.tiles_coordinates), self.num_tiles):
            r = random.randint(0, 1)
            if self.beginning > 0:
                r = 0
                self.beginning = self.beginning - 1
            self.tiles_coordinates.append((last_x, last_y))
            start_index = -int(self.num_vertical_lines / 2) + 1
            end_index = start_index + self.num_vertical_lines - 2
            if last_x <= start_index:
                r = 1
            if last_x >= end_index:
                r = 2
            if r == 1:
                last_x = last_x + 1
                self.tiles_coordinates.append((last_x, last_y))
                last_y = last_y + 1
                self.tiles_coordinates.append((last_x, last_y))
            if r == 2:
                last_x = last_x - 1
                self.tiles_coordinates.append((last_x, last_y))
                last_y = last_y + 1
                self.tiles_coordinates.append((last_x, last_y))

            last_y = last_y + 1

    def update_tiles(self):
        for i in range(self.num_tiles):
            tile = self.tiles[i]
            ti_x, ti_y = self.tiles_coordinates[i]
            x_min, y_min = self.get_tile_coordinates(ti_x, ti_y)
            x_max, y_max = self.get_tile_coordinates(ti_x + 1, ti_y + 1)

            x1, y1 = self.transform(x_min, y_min)
            x2, y2 = self.transform(x_min, y_max)
            x3, y3 = self.transform(x_max, y_max)
            x4, y4 = self.transform(x_max, y_min)

            tile.points = (x1, y1, x2, y2, x3, y3, x4, y4)

    def get_line_x_from_index(self, index):
        offset = index - 0.5
        spacing = self.vertical_line_spacing * self.width
        central_line_x = self.perspective_point_x
        line_x = central_line_x + offset * spacing + self.current_offset_x
        return line_x

    def update_vertical_lines(self):
        start_index = -int(self.num_vertical_lines / 2) + 1
        end_index = start_index + self.num_vertical_lines
        for i in range(start_index, end_index):
            line_x = self.get_line_x_from_index(i)
            x1, y1 = self.transform(line_x, 0)
            x2, y2 = self.transform(line_x, self.height)
            self.vertical_lines[i].points = (x1, y1, x2, y2)

    def get_line_y_from_index(self, index):
        spacing = self.horizontal_line_spacing * index
        line_y = self.height * spacing - self.current_offset_y
        return line_y

    def update_horizontal_lines(self):
        start_index = -int(self.num_vertical_lines / 2) + 1
        end_index = start_index + self.num_vertical_lines - 1

        x_min = self.get_line_x_from_index(start_index)
        x_max = self.get_line_x_from_index(end_index)

        for i, line in enumerate(self.horizontal_lines):
            line_y = self.get_line_y_from_index(i)
            x1, y1 = self.transform(x_min, line_y)
            x2, y2 = self.transform(x_max, line_y)
            line.points = (x1, y1, x2, y2)

    def update(self, dt):
        speed_y = self.speed_y * self.height / 400
        speed_x = self.speed_x * self.width / 800
        time_factor = dt * self.refresh_rate
        self.update_ship()
        self.update_vertical_lines()
        self.update_horizontal_lines()
        self.update_tiles()

        if not self.game_over and self.game_start:
            x, y = self.perspective_point_x, self.perspective_point_y
            x = x + self.vx
            y = y + self.vy
            if x >= self.fix_x + dp(160) or x <= self.fix_x - dp(160):
                self.vx = -self.vx
            if y >= self.fix_y + dp(100) or y <= self.fix_y - dp(200):
                self.vy = -self.vy
            self.perspective_point_x, self.perspective_point_y = (x, y)
            print(self.fix_x, self.fix_y, x, y, self.perspective_point_x, self.perspective_point_y)

            self.current_offset_y = (speed_y * time_factor / 4) + self.current_offset_y
            spacing = self.horizontal_line_spacing * self.height

            while self.current_offset_y > spacing:
                self.current_offset_y = self.current_offset_y - spacing
                self.current_loop_y = self.current_loop_y + 1
                self.generate_tiles_coordinates()

            if self.go_left:
                self.current_offset_x = (speed_x * time_factor / 4) + self.current_offset_x
            if self.go_right:
                self.current_offset_x = (-speed_x * time_factor / 4) + self.current_offset_x

            self.score_txt = f"SCORE: {self.current_loop_y}"
            self.speed_y = 4 + int((time.time() - self.start_time) / 10)

        if not self.check_collisions_ship() and not self.game_over:
            self.menu_title = "G  A  M  E    O  V  E  R"
            self.menu_button = "RESTART"
            self.game_over = True
            self.menu_widget.opacity = 1
            self.music1_sound.stop()
            self.gameover_impact_sound.play()
            Clock.schedule_once(self.play_game_over_sound, 1)

    def play_game_over_sound(self, dt):
        if self.game_over:
            self.gameover_voice_sound.play()

    def on_menu_button_press(self):
        if self.game_over:
            self.restart_sound.play()
            self.music1_sound.stop()

        else:
            self.begin_sound.play()

        self.reset_game()
        self.game_start = True
        self.menu_widget.opacity = 0


class galaxy_game(App):
    pass


galaxy_game().run()
