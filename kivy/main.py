from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.properties import NumericProperty
from kivy.clock import Clock
from kivy import platform
import random
# Розмір вікна (для ПК, на Android не впливає)
if platform == "android":
    Window.size = (450, 900)

class Fish(Image):
    hp_current = 0
    timer_hide = None
    timer_show = None

    def on_kv_post(self, base_widget):
        self.GAME_SCREEN = self.parent.parent
        return super().on_kv_post(base_widget)

    def new_fish(self, *args):
        self.source = "assets/images/fish.png"
        self.hp_current = 10
        self.show_fish()

    def show_fish(self, *args):
        self.opacity = 1
        time_visible = random.uniform(0.5, 2.0)
        self.timer_hide = Clock.schedule_once(self.hide_fish, time_visible)

    def hide_fish(self, *args):
        self.opacity = 0
        time_hidden = random.uniform(1.0,3.0)
        self.timer_show = Clock.schedule_once(self.show_fish, time_hidden)

    def stop_timers(self):
        if self.timer_hide:
            self.timer_hide.cancel()
        if self.timer_show:
            self.timer_show.cancel()

    def defeated(self):
        self.opacity = 0
        self.stop_timers()

        # КЛІК ПО РИБІ
    def on_touch_down(self, touch):
        # Якщо клік був не по рибі або вона прозора — передаємо клік далі
        if not self.collide_point(*touch.pos) or not self.opacity:
            return super().on_touch_down(touch)

        self.hp_current -= 1
        self.GAME_SCREEN.score += 1

        if self.hp_current <= 0:
            self.defeated()
            Clock.schedule_once(self.GAME_SCREEN.level_complete, 1.2)
        else:
            self.stop_timers()
            self.hide_fish()

        # Повертаємо True, щоб система знала: "Клік був влучним, ми його обробили!"
        return True
    
class MenuScreen(Screen):
    # Перехід до екрана гри
    def go_game(self, *args):
        self.manager.current = "game"

    # Перехід до екрана налаштувань
    def go_settings(self, *args):
        self.manager.current = "settings"

    # Вихід з програми
    def exit_app(self, *args):
        app.stop()


class GameScreen(Screen):
    score = NumericProperty(0)
    def on_pre_enter(self, *args):
        self.score = 0
        self.ids.level_complete.opacity = 0
        return super().on_pre_enter(*args)

    def on_enter(self, *args):
       self.start_game()
       return super().on_enter(*args)
    
    def start_game(self):
        self.ids.fish.new_fish()

    def level_complete(self, *args):
        self.ids.level_complete.opacity = 1

    # Повернення до меню
    def go_menu(self, *args):
        self.manager.current = "menu"

    def on_touch_down(self, touch):
        if super().on_touch_down(touch):
            return True
        if self.ids.fish.hp_current > 0:
            self.score = max(0, self.score - 1)
        return True


class SettingsScreen(Screen):
    # Повернення до меню
    def go_menu(self, *args):
        self.manager.current = "menu"


class ClickerApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MenuScreen(name="menu"))
        sm.add_widget(GameScreen(name="game"))
        sm.add_widget(SettingsScreen(name="settings"))
        return sm


app = ClickerApp()
app.run()