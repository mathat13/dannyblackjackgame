from pathlib import Path

import pyglet
import pyglet.gl as gl
import pyglet.clock as clock
import simpleaudio as sa
import Model as Mod
import Notifiable
import sys
import random
import sound.sound as snd
import pathlib


class BlackJackWindow(pyglet.window.Window, Notifiable.Notifiable):
    MUSIC_ON = False
    WINDOW_WIDTH = 1400
    WINDOW_HEIGHT = 800
    ACTIONS = ["retry", "hit", "stand", "split"]
    CARD_COLOUR = "red"
    TEMP_MONEY = 100
    BACKGROUND_RGB = [39, 119, 20]
    TEXT_COLOUR = (255, 255, 51, 175)
    TEMP_IS_HIDDEN = False  # TODO replace with model reference

    def __init__(self, config):
        super().__init__(config=config, width=self.WINDOW_WIDTH, height=self.WINDOW_HEIGHT, visible=False)
        self.background_colour = tuple(self.BACKGROUND_RGB * 4)
        self.img_base = ImageBase()
        self.card_width, self.card_height = self.WINDOW_WIDTH / 12, self.WINDOW_HEIGHT / 4
        self.cards = []
        self.btn_width, self.btn_height = self.WINDOW_WIDTH / 10, self.WINDOW_HEIGHT / 8
        self.set_location(200, 30)
        self.btn_tints = [255, 255, 255, 255, 255, 255]
        if random.random() < .1:
            self.ACTIONS.append("nice")
        self.card_paddding = self.card_width / 4
        self.background_batch = pyglet.graphics.Batch()
        self.background_batch.add(4, pyglet.gl.GL_QUADS, None,
                                  ('v2i', (0, 0, self.width, 0,
                                           self.width, self.height, 0, self.height)),
                                  ('c3B', self.background_colour))
        self.batch = pyglet.graphics.Batch()
        self.btns = []
        self.model = Mod.Model(self)
        clock.set_fps_limit(1.0 / 60)
        pyglet.clock.schedule_interval(self.tick, 1.0 / 60)
        self.txt, self.money_lbl, self.lbl = "", None, None
        self.notify("Welcome to BlackJack!")
        self.update_frame()
        self.set_visible(True)
        if self.MUSIC_ON:
            self.play_music()

    def tick(self, dt=0):
        for i in range(len(self.btn_tints)):
            if self.btn_tints[i] < 255:
                self.btn_tints[i] += 50
                self.dispatch_event('on_draw')

    def notify(self, txt=""):
        if txt == "retry":
            self.cards = [BJCard(''.join(self.model.playerhand[i]),
                                 self.batch,
                                 True,
                                 self.card_width / 2 + i * self.card_paddding + i * self.card_width,
                                 self.card_height / 2, self.card_width, self.card_height,
                                 self.img_base) for i in range(0, len(self.model.playerhand))] \
                         + [BJCard(''.join(self.CARD_COLOUR + "_back"
                                           if self.model.is_hidden and i == 0
                                           else self.model.dealerhand[i]),
                                   self.batch,
                                   True,
                                   self.card_width / 2 + i * self.card_paddding + i * self.card_width,
                                   self.card_paddding + self.WINDOW_HEIGHT / 2,
                                   self.card_width, self.card_height,
                                   self.img_base) for i in range(0, len(self.model.dealerhand))]
        elif txt == "hit":
            ref_index = len(self.model.playerhand) - 1
            self.cards.append(BJCard(''.join(self.model.playerhand[ref_index]),
            self.batch,
            True,
            self.card_width / 2 + ref_index * self.card_paddding + ref_index * self.card_width,
            self.card_height / 2, self.card_width, self.card_height,
            self.img_base))
        elif txt == "stand":
            self.cards[len(self.model.playerhand)] = BJCard(''.join(self.model.dealerhand[0]),
                                   self.batch,
                                   True,
                                   self.card_width / 2,
                                   self.card_paddding + self.WINDOW_HEIGHT / 2,
                                   self.card_width, self.card_height,
                                   self.img_base)
            self.cards[len(self.model.playerhand)].x = self.cards[len(self.model.playerhand)].target_x
            self.cards[len(self.model.playerhand)].y = self.cards[len(self.model.playerhand)].target_y
            self.tick()
        elif txt == "Dealer thinking":
            self.cards += [BJCard(''.join(self.model.dealerhand[len(self.model.dealerhand)-1]),
                                   self.batch,
                                   True,
                                   self.card_width / 2 + (len(self.model.dealerhand)-1) * self.card_paddding + (len(self.model.dealerhand)-1) * self.card_width,
                                   self.card_paddding + self.WINDOW_HEIGHT / 2,
                                   self.card_width, self.card_height,
                                   self.img_base)]


        self.is_changed = True

        if len(txt) > 0 and txt not in self.ACTIONS:
            self.txt = txt
        # remove one of dispatch event, solve on joe's
        self.dispatch_events()
        self.dispatch_event('on_draw')
        self.flip()
        self.dispatch_events()

    def on_mouse_press(self, x, y, btn, modifiers):
        for i in range(len(self.btns)):
            btn = self.btns[i]
            if btn.x <= x <= btn.x + btn.width and btn.y <= y <= btn.y + btn.height \
                    and (True if self.ACTIONS[i] == "nice" else self.model.BUTTON_DICT[self.ACTIONS[i]]):
                if btn.act_name == "nice":
                    for x in range(0, 2):
                        wind = snd.OtherWindow(config=self.config)
                        wind.set_location(random.randint(0, 1000), random.randint(0, 1000))
                        wind.dispatch_events()
                    break
                self.btn_tints[i] = 105
                self.dispatch_event('on_draw')
                self.make_sound(btn.act_name)
                self.model.notify(btn.act_name)
                self.notify(btn.act_name)
                break

    def update_frame(self):
        for card in self.cards:
            card.move_towards_target_x()
        self.money_lbl = pyglet.text.Label("£" + str(self.TEMP_MONEY),
                                           font_name='Impact',
                                           font_size=36,
                                           width=self.btn_width, height=self.btn_height,
                                           x=self.width // 15, y=self.height - self.btn_height,
                                           anchor_x='center', anchor_y='center',
                                           color=self.TEXT_COLOUR)
        pyglet.font.add_file('res/haarlem_deco.ttf')
        haarlem_deco = pyglet.font.load('Haarlem Deco DEMO')
        self.lbl = pyglet.text.Label(self.txt,
                                     font_name='Haarlem Deco DEMO',
                                     font_size=36,
                                     width=self.btn_width, height=self.btn_height,
                                     x=self.width // 3, y=self.height - self.btn_height,
                                     anchor_x='center', anchor_y='center',
                                     color=self.TEXT_COLOUR)
        self.btns = [BJButton(self.ACTIONS[i], self.batch, self.WINDOW_WIDTH - 1.5 * self.btn_width,
                              self.WINDOW_HEIGHT - 1.5 * self.btn_height - 1.5 * i * self.btn_height,
                              self.btn_width,
                              self.btn_height,
                              True if self.ACTIONS[i] == "nice" else self.model.BUTTON_DICT[self.ACTIONS[i]],
                              self.img_base) for i in range(0, len(self.ACTIONS))]
        for i in range(0, len(self.btn_tints)):
            tint = self.btn_tints[i]
            if tint < 255:
                self.btns[i].color = (tint, tint, tint)

    def on_draw(self):
        self.update_frame()
        self.clear()
        self.background_batch.draw()
        self.money_lbl.draw()
        self.lbl.draw()
        self.batch.draw()

    @classmethod
    def make_sound(cls, sound_name):
        if sound_name == "":
            return
        wave_obj = sa.WaveObject.from_wave_file("sound/" + sound_name + ".wav")
        wave_obj.play()

    @classmethod
    def play_music(cls):
        wave_obj = sa.WaveObject.from_wave_file("sound/cantina_song.wav")
        wave_obj.play()


class ImageBase:
    def __init__(self):
        img_dir = pathlib.Path('img')
        self.img_dict = dict([])
        file: Path
        for file in img_dir.iterdir():
            path = str(file)
            key = path.replace("img\\", "").replace(".png", "")
            stream = open(path, 'rb')
            img = pyglet.image.load(path, file=stream)
            self.img_dict.update({key: img})


class BJCard(pyglet.sprite.Sprite):
    def __init__(self, img_name, batch, is_showing, target_x, target_y, width, height, img_base: ImageBase):
        img = img_base.img_dict[img_name]
        super().__init__(img, batch=batch)
        self.scale_x = width / self.width
        self.scale_y = height / self.height
        self.is_showing = is_showing
        self.target_x = target_x
        self.target_y = target_y
        self.x = BlackJackWindow.WINDOW_WIDTH
        self.y = BlackJackWindow.WINDOW_HEIGHT

    def set_start_coordinates(self, x, y):
        self.x = BlackJackWindow.WINDOW_WIDTH
        self.y = BlackJackWindow.WINDOW_HEIGHT

    def move_towards_target_x(self):
        self.x += (self.target_x - self.x)/4
        self.y += (self.target_y - self.y)/4


class BJButton(BJCard):
    def __init__(self, act_name, batch, x, y, width, height, is_active, img_base):
        super().__init__("btn_" + act_name, batch, None, x, y, width, height, img_base)
        self.act_name = act_name
        self.set_start_coordinates(x, y)
        if not is_active:
            self.opacity = 50

    def set_start_coordinates(self, x, y):
        self.x, self.y = x, y



def main():
    print("Python version used in program is", sys.version)
    config = gl.Config()
    wind = BlackJackWindow(config=config)
    pyglet.app.run()


if __name__ == '__main__':
    main()
