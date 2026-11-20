# This file was created by Nathan Kim
# Code inspired by game dev Chris Bradfield who was inspired by Notch

#imports python & changes abbreviation to pg
import pygame as pg
import ast

from os import path
#imports sprites
from sprites import *

#imports settings
from settings import *

from utils import *

# Why are wer making game a class?
# Why is it capitalized
# What is init?
# What is pass?

# Data types: boolean, JSON, integer, strings
# Input (events): Keyboard, mouse, right click, voice,
# power button, eye tracking, camera, gyroscoping, electrostatic, location, volume
# microphone - zelda game where you blow out a candle with the mic

# Process: cursor position, position of the player, score, enemy position, velocity,
# aim in FPS,

# Output: Graphics - things are drawn, sounds: jump, power, walking, haptics

# GOALS: Explore the map, fish, collect different fish, and improve your fish.
# RULES: Use F near a lake to fish. Use E near the merchant to open the store.
# FEEDBACK: The game displays messages when you buy, sell, or cannot afford an item.
# FREEDOM: Choose which fish to keep, sell, and which items to buy.


# DESIGN GOALS
# 1. Goals: Collect rare fish, level them up, and evolve them.
# 2. Rules: Fish can only be caught when their health is below 10%.
# 3. Feedback: Display messages when catching fish, winning battles,
#    buying items, and selling fish.
# 4. Freedom: Allow players to explore, choose which fish to keep,
#    buy items, and decide which fish to use in battle.
# creating the class game


class Game:
    def __init__(self):
        pg.init()
        pg.mixer.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        print("game initialized...")
        pg.display.set_caption(TITLE)
        self.running = True
        self.playing = True
        self.clock = pg.time.Clock()
        self.score = 0
        self.high_score = 0
        self.shop_open = False
        self.shop_message = ""
        self.show_fish = False

    # adding the images and audio
    def load_data(self, map):
        self.game_dir = path.dirname(__file__)
        self.game_save_file = path.join(self.game_dir, "highscore.txt")
        self.progress_save_file = path.join(self.game_dir, "savegame.txt")

        self.img_dir = path.join(self.game_dir, 'images')
        # sound handling
        self.snd_dir = path.join(self.game_dir, 'audio')
        self.pickup_snd = pg.mixer.Sound(path.join(self.snd_dir, "audio_pickup.wav"))
        self.jump_sound = pg.mixer.Sound(path.join(self.snd_dir, "audio_pickup.wav"))
        self.map = Map(path.join(self.game_dir, map))

        try:
            with open(self.game_save_file, 'x', encoding="utf-8") as file:
                file.write("hello world!")
            print("file created successfully!")
        except FileExistsError:
            print("File already exists")

        with open(self.game_save_file, 'r') as file:
            try:
                self.high_score = int(file.read())
            except:
                # self.high_score = 0
                print("high score not read...")

    def new(self):
        #loading the map and all of the sprites
        self.load_data('level1.txt')
        print(self.map.data)
        self.all_sprites = pg.sprite.Group()
        self.all_walls = pg.sprite.Group()
        self.all_coins = pg.sprite.Group()
        self.all_mobs = pg.sprite.Group()
        self.all_particles = pg.sprite.Group()
        self.all_floors = pg.sprite.Group()
        self.all_lakes = pg.sprite.Group()
        self.all_merchants = pg.sprite.Group()
        self.all_houses = pg.sprite.Group()

        # player fish and items
        self.fish_collection = [Fish()]
        self.nets = [Net()]
        self.evolution_stones = 0

        #enumerating the rows and columns of the map to create all of the walls, mobs, and coins
        #Adding floor as well
        for row, tiles in enumerate(self.map.data):
            for col, tile in enumerate(tiles):
                if tile == '.':
                    floor1(self, col, row)
                if tile == 'G':
                    floor2(self, col, row)

        for row, tiles in enumerate(self.map.data):
            for col, tile in enumerate(tiles):
                if tile == '1':
                    Wall(self, col, row)
                if tile == ';':
                    Mob(self, col, row)
                if tile == 'C':
                    Coin(self, col, row)
                #added lake now
                if tile == 'L':
                    Lake(self, col, row)
                if tile == 'M':
                    Merchant(self, col, row)
                if tile == 'H':
                    house(self, col, row)

        for row, tiles in enumerate(self.map.data):
            for col, tile in enumerate(tiles):
                if tile == 'P':
                    self.player = Player(self, col, row)

        # Load saved progress after creating the player and starting inventory.
        self.load_game()

        pg.mixer.music.load(path.join(self.snd_dir, "bg.mp3"))
        pg.mixer.music.play(loops=-1)

    # Save the player's progress in a separate JSON file.
    def save_game(self):
        if not hasattr(self, "player"):
            return

        save_data = {
            "coins": self.player.coins,
            "score": self.score,
            "player_x": self.player.pos.x,
            "player_y": self.player.pos.y,
            "evolution_stones": self.evolution_stones,
            "nets": [{"name": net.name, "uses": net.uses} for net in self.nets],
            "fish": []
        }

        for fish in self.fish_collection:
            save_data["fish"].append({
                "name": fish.name,
                "rarity": fish.rarity,
                "weight": fish.weight,
                "health": fish.health,
                "max_health": fish.max_health,
                "attack": fish.attack,
                "traits": fish.traits,
                "level": fish.level,
                "xp": fish.xp,
                "xp_to_next_level": fish.xp_to_next_level,
                "evolution_stage": fish.evolution_stage,
                "evolutions": fish.evolutions,
                "crit_chance": fish.crit_chance
            })

        try:
            with open(self.progress_save_file, "w", encoding="utf-8") as file:
                file.write(str(save_data))
        except (OSError, TypeError) as error:
            print("Could not save game:", error)

    # Restore saved progress. If there is no save file, keep the starter inventory.
    def load_game(self):
        if not path.exists(self.progress_save_file):
            return

        try:
            with open(self.progress_save_file, "r", encoding="utf-8") as file:
                save_data = ast.literal_eval(file.read())

            self.player.coins = save_data.get("coins", 0)
            self.score = save_data.get("score", 0)
            if "player_x" in save_data and "player_y" in save_data:
                self.player.pos.x = save_data["player_x"]
                self.player.pos.y = save_data["player_y"]
                self.player.hit_rect.center = (self.player.pos.x, self.player.pos.y)
                self.player.rect.center = self.player.hit_rect.center
            self.evolution_stones = save_data.get("evolution_stones", 0)
            self.nets = [Net(item.get("name", "Basic Net"), item.get("uses", 10))
                         for item in save_data.get("nets", [])]

            saved_fish = save_data.get("fish", [])
            if saved_fish:
                self.fish_collection = []
                for item in saved_fish:
                    fish = Fish()
                    for attribute in ("name", "rarity", "weight", "health", "max_health",
                                      "attack", "traits", "level", "xp", "xp_to_next_level",
                                      "evolution_stage", "evolutions", "crit_chance"):
                        if attribute in item:
                            setattr(fish, attribute, item[attribute])
                    self.fish_collection.append(fish)

            if not self.nets:
                self.nets = [Net()]

            print("Game progress loaded!")
        except (OSError, ValueError, TypeError, KeyError) as error:
            print("Could not load save file:", error)

    def can_fish(self):
        for lake in self.all_lakes:
            if lake.rect.inflate(TILESIZE * 2, TILESIZE * 2).colliderect(self.player.rect):
                return True
        return False

    # checking whether the player is close enough to a merchant
    def can_shop(self):
        for merchant in self.all_merchants:
            if merchant.rect.inflate(TILESIZE * 2, TILESIZE * 2).colliderect(self.player.rect):
                return True
        return False

    # finding a net that still has uses remaining
    def get_net(self):
        for net in self.nets:
            if net.uses > 0:
                return net
        return None

    # opening the merchant store and handling purchases and sales
    def shop_events(self, key):
        if key == pg.K_ESCAPE or key == pg.K_e:
            self.shop_open = False
            self.show_fish = False
            return

        if key == pg.K_n:
            if self.player.coins >= 5:
                self.player.coins -= 5
                self.nets.append(Net())
                self.shop_message = "Bought a Basic Net for 5 coins."
            else:
                self.shop_message = "You need 5 coins to buy a net."

        elif key == pg.K_s:
            if self.player.coins >= 15:
                self.player.coins -= 15
                self.evolution_stones += 1
                self.shop_message = "Bought an Evolution Stone for 15 coins."
            else:
                self.shop_message = "You need 15 coins to buy an Evolution Stone."

        elif key == pg.K_v:
            self.show_fish = not self.show_fish
            self.shop_message = "Press a fish number to sell it." if self.show_fish else ""

        elif self.show_fish and pg.K_1 <= key <= pg.K_9:
            fish_number = key - pg.K_1
            if fish_number < len(self.fish_collection):
                if len(self.fish_collection) <= 1:
                    self.shop_message = "You must keep at least one fish."
                else:
                    fish = self.fish_collection[fish_number]
                    sell_prices = {
                        "common": 5,
                        "uncommon": 10,
                        "rare": 20,
                        "legendary": 50,
                        "impossible": 100
                    }
                    price = sell_prices.get(fish.rarity, 5)
                    self.player.coins += price
                    self.fish_collection.pop(fish_number)
                    self.shop_message = "Sold " + fish.name + " for " + str(price) + " coins."
            else:
                self.shop_message = "There is no fish with that number."

        # Save immediately after a purchase or sale.
        self.save_game()

    def run(self):
        self.playing = True
        while self.playing:
            #adding a clock to later use for the game
            self.dt = self.clock.tick(FPS) / 1000
            self.events()
            self.update()
            self.draw()

    #seeing if the user has quit the game or not as well as if the user has pressed the f key to fish and are near a lake
    def events(self):
        for event in pg.event.get():
            if event.type == pg.KEYDOWN:
                if self.shop_open:
                    self.shop_events(event.key)

                elif event.key == pg.K_e:
                    if self.can_shop():
                        self.shop_open = True
                        self.shop_message = "Welcome! Choose an option below."
                    else:
                        print("You need to be near a merchant!")

                elif event.key == pg.K_f:
                    if self.can_fish():
                        print("You can fish here!")
                    else:
                        print("You need to be near a lake!")

            if event.type == pg.QUIT:
                self.save_game()
                with open(self.game_save_file, 'w') as f:
                    f.write(str(max(self.high_score, self.score)))
                if self.playing:
                    self.playing = False
                self.running = False

    # drawing text on the screen
    def draw_text(self, text, size, color, x, y):
        font_name = pg.font.match_font('arial')
        font = pg.font.Font(font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.topleft = (x, y)
        self.screen.blit(text_surface, text_rect)

    #updating the screen and all of the sprites
    def update(self):
        self.all_sprites.update()

    #drawing the screen and all of the sprites
    def draw(self):
        # this order matters: the first things are on the bottom because they are the first to be drawn
        # the last lines in this method are drawn on top or last
        self.screen.fill(GRASS_GREEN)
        self.all_sprites.draw(self.screen)

        # drawing the merchant store over the game
        if self.shop_open:
            overlay = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
            overlay.fill((0, 0, 0, 190))
            self.screen.blit(overlay, (0, 0))

            self.draw_text("MERCHANT STORE", 32, WHITE, 30, 25)
            self.draw_text("Coins: " + str(self.player.coins), 22, WHITE, 30, 75)
            self.draw_text("Nets owned: " + str(len(self.nets)), 18, WHITE, 400, 75)
            self.draw_text("Evolution Stones: " + str(self.evolution_stones), 18, WHITE, 400, 100)
            self.draw_text("N: Buy Basic Net (10 uses)  |  5 coins", 20, WHITE, 30, 125)
            self.draw_text("S: Buy Evolution Stone  |  15 coins", 20, WHITE, 30, 160)
            self.draw_text("V: View and sell fish", 20, WHITE, 30, 195)
            self.draw_text("E or ESC: Close store", 20, WHITE, 30, 230)

            if self.show_fish:
                self.draw_text("YOUR FISH", 22, WHITE, 30, 280)
                for i, fish in enumerate(self.fish_collection[:9]):
                    self.draw_text(
                        str(i + 1) + ": " + fish.name + " (" + fish.rarity + ")",
                        18, WHITE, 30, 315 + i * 25
                    )
                self.draw_text("Press the fish number to sell it.", 18, WHITE, 400, 315)

            self.draw_text(self.shop_message, 18, YELLOW, 30, HEIGHT - 45)

        pg.display.flip()


if __name__ == "__main__":
    g = Game()

while g.running:
    g.new()
    g.run()

# SOURCES
# Original game engine: Class repository.
# Pygame documentation: https://www.pygame.org/docs/
# Python documentation: https://docs.python.org/3/
# AI assistance: OpenAI ChatGPT, used for debugging,
# programming assistance, and development suggestions.