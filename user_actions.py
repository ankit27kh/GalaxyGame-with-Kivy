from kivy.uix.relativelayout import RelativeLayout


def keyboard_closed(self):
    self._keyboard.unbind(on_key_down=self.on_keyboard_down)
    self._keyboard.unbind(on_key_up=self.on_keyboard_up)
    self._keyboard = None


def on_keyboard_down(self, keyboard, keycode, text, modifiers):
    if keycode[1] == 'left':
        self.go_left = True
    elif keycode[1] == 'right':
        self.go_right = True
    return True


def on_keyboard_up(self, keyboard, keycode):
    self.go_left = self.go_right = False
    return True


def on_touch_down(self, touch):
    if not self.game_over and self.game_start:
        if touch.x < self.width / 2:
            self.go_left = True
        else:
            self.go_right = True
    return super(RelativeLayout, self).on_touch_down(touch)


def on_touch_up(self, touch):
    self.go_left = self.go_right = False
