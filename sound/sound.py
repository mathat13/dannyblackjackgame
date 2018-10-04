import pyglet
import random


class OtherWindow(pyglet.window.Window):
    def __int__(self, config):
        super().__init__(config=config, width=200, height=200, visible=True)

    def trigger(self):
        self.dispatch_events()
        self.minimize()

    def on_close(self):
        for x in range(0, 15):
            wind = OtherWindow(config=self.config)
            wind.set_location(random.randint(0, 1400), random.randint(0, 800))
            wind.dispatch_events()

    def on_draw(self):
        self.clear()
        lbl = pyglet.text.Label("Fuck You Joe!!!!!!!!",
                                     font_name='Impact',
                                     font_size=36,
                                     width=100, height=100,
                                     x=300, y=250,
                                     anchor_x='center', anchor_y='center',
                                     color=(255, 255, 255, 255))
        lbl.draw()