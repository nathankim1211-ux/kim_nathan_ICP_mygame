from random import randint

import pygame as pg
from settings import *
from pygame.sprite import Sprite
from utils import *

from os import path

vec = pg.math.Vector2

#collision detection
def collide_hit_rect(one, two):
    return one.hit_rect.colliderect(two.rect)

def collide_with_walls(sprite, group, dir):
    # check for x collision
    if dir == 'x':
        # checking to see if we've collided with hitrects
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            # this line checks to see if we're to the left of the wall
            if hits[0].rect.centerx > sprite.hit_rect.centerx:
                # reposition the player (sprite) to the left side of the wall
                sprite.pos.x = hits[0].rect.left - sprite.hit_rect.width / 2
            if hits[0].rect.centerx < sprite.hit_rect.centerx:
                sprite.pos.x = hits[0].rect.right + sprite.hit_rect.width / 2 
            sprite.vel.x = 0
            sprite.hit_rect.centerx = sprite.pos.x
    if dir == 'y':
        # checking to see if we've collided with hitrects
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            # this line checks to see if we're above the wall
            if hits[0].rect.centery > sprite.hit_rect.centery:
                # reposition the player (sprite) to the top of the wall
                sprite.pos.y = hits[0].rect.top - sprite.hit_rect.height / 2
            if hits[0].rect.centery < sprite.hit_rect.centery:
                sprite.pos.y = hits[0].rect.bottom + sprite.hit_rect.height / 2 
            sprite.vel.y = 0
            sprite.hit_rect.centery = sprite.pos.y

#making class player, wall, coin, and mob
class Player(Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        Sprite.__init__(self, self.groups)
        self.game = game
        self.spritesheet = Spritesheet(path.join(self.game.img_dir, "sprite_sheet.png"))
        self.load_images()
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image = self.spritesheet.get_image(0,0,TILESIZE, TILESIZE)
        self.image.set_colorkey(BLACK)
        # self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.hit_rect = PLAYER_HIT_RECT
        self.vel = vec(0,0)
        self.acc = vec(0,0)
        self.pos = vec(x*TILESIZE,y*TILESIZE)
        self.spawn_pos = self.pos.copy()
        # animation stuff
        self.last_update = 0
        self.current_frame = 0
        self.dir = "none"
        self.coins = 0
        self.jumping = False
        print('player instantiated')
        print(self.pos)

#making the keys for player movement and the direction of the player
    def get_keys(self):
        # self.vel = vec(0,0)
        self.dir = "none"
        keys = pg.key.get_pressed()

        # stop player movement while the merchant store is open
        if self.game.shop_open:
            self.acc = vec(0, 0)
            self.vel = vec(0, 0)
            return

        if keys[pg.K_LEFT] or keys[pg.K_a]:
            self.acc.x = -PLAYER_SPEED
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            self.dir = "right"
            self.acc.x = PLAYER_SPEED
        if keys[pg.K_UP] or keys[pg.K_w]:
            self.acc.y = -PLAYER_SPEED
        if keys[pg.K_DOWN] or keys[pg.K_s]:
            self.acc.y = PLAYER_SPEED
        if keys[pg.K_p]:
            self.pos = self.spawn_pos.copy()
            self.vel = vec(0, 0)
            self.acc = vec(0, 0)
            self.hit_rect.center = self.pos
            self.rect.center = self.pos
            # check to see if player is moving diagonaly
        # if keys[pg.K_SPACE]:
        #     self.jump()
        # if self.vel.x != 0 and self.vel.y != 0:
            self.vel *= 0.7071
    def animate(self):
        # use the time element to get now
        now = pg.time.get_ticks()
        if self.dir == "none":
            if now - self.last_update > 350:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.idle_frames)
                bottom = self.rect.bottom
                self.image = self.idle_frames[self.current_frame]
                self.image.set_colorkey(BLACK)
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom
        elif self.dir == "right":
            pass
    def load_images(self):
        self.idle_frames = [self.spritesheet.get_image(0,0,TILESIZE, TILESIZE),
                            self.spritesheet.get_image(TILESIZE,0,TILESIZE, TILESIZE)
                            ]
        self.run_frames = [self.spritesheet.get_image(0,0,TILESIZE, TILESIZE),
                            self.spritesheet.get_image(TILESIZE,0,TILESIZE, TILESIZE)
                            ]
    #updating the player position and checking for collisions with walls and coins
    def jump(self):
        # jump only if standing something
        self.rect.y += 2
        hits = pg.sprite.spritecollide(self, self.game.all_walls, False)
        self.rect.y -= 2
        if hits and not self.jumping:
            self.game.jump_sound.play()
            self.jumping = True
            self.vel.y = -PLAYER_JUMP
    
    def is_jumping(self):
        if self.vel.y > 0:
            hits = pg.sprite.spritecollide(self, self.game.all_walls, False)
            if hits:
                self.jumping = False

    def update(self):
        #added animation
        self.animate()
        #added jumping
        self.is_jumping()
        #giving gravity so it constantly falls unless jumping
        self.acc = vec(0,0)
        self.get_keys()
        self.acc.x += self.vel.x * PLAYER_FRIC
        self.acc.y += self.vel.y * PLAYER_FRIC
        self.vel += self.acc
        if abs(self.vel.x) < 0.1:
            self.vel.x = 0
        if abs(self.vel.y) < 0.1:
            self.vel.y = 0
        # self.rect.center = self.pos
        self.pos += self.vel + 0.5 * self.acc
        # self.pos += self.vel * self.game.dt + 0.5 * self.acc
        # self.pos += self.vel * self.game.dt
        hits = pg.sprite.spritecollide(self, self.game.all_coins, True)
        if hits:
            for i in range(25):
                p = Particle(self.game, hits[0].rect.centerx, hits[0].rect.centery)
            self.coins += 1
            self.game.pickup_snd.play()
            self.game.score += 1
        self.hit_rect.centerx = self.pos.x
        collide_with_walls(self, self.game.all_walls, 'x')
        self.hit_rect.centery = self.pos.y
        if collide_with_walls(self, self.game.all_walls, 'y'):
            self.jumping = False
        self.rect.center = self.hit_rect.center

    
# making class wall
class Wall(Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.all_walls
        Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.vx, self.vy = 0,0
        self.x = x*TILESIZE
        self.y = y*TILESIZE
        self.rect.x = self.x
        self.rect.y = self.y
        # print("wall initialized")
        # print(self.rect.x)
        # print(self.rect.y)
# class coin
class Coin(Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.all_coins
        Sprite.__init__(self, self.groups)
        self.game = game
        #size of coin
        self.image = pg.Surface((TILESIZE, TILESIZE))
        pg.draw.circle(self.image, YELLOW, (TILESIZE//2, TILESIZE//2), TILESIZE//2)
        self.rect = self.image.get_rect()
        self.vx, self.vy = 0,0
        self.x = x*TILESIZE
        self.y = y*TILESIZE
        self.rect.x = self.x
        self.rect.y = self.y
#making the particles for the coin
class Particle(Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.all_particles
        Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((5, 5))
        #particle color
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.vel = vec(randint(-180, 180), randint(-180, 180))
        self.pos = vec(x, y)
        self.speed = randint(1, 3)
        self.cooldown = Cooldown()
        self.cooldown.event_time = floor(pg.time.get_ticks()/1000)
        # print(self.pos.x)
        # print(self.pos.y)
        # print(str(len(self.game.all_particles)))

    def update(self):
        self.cooldown.ticking()
        self.pos += self.vel * self.speed * self.game.dt
    #killing the particle when cooldown is more than 1
        if self.cooldown.delta > 1:
            self.kill()
            #goes and update the particles on to the screen
        self.rect.x = self.pos.x
        self.rect.y = self.pos.y

#makign floor class 1 and 2 for each to have their own sprite from the grass.png file
#copied from wall and mob and took a bunch of code from them
#also had do ask the CS50 to get the positioning for the grass.png
class floor1(Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.image.load(path.join(self.game.img_dir, "grass.png")).convert()
        #got this line from CS50
        self.image = self.image.subsurface((0, 0, 32, 32))
        self.rect = self.image.get_rect()
        self.vx, self.vy = 0,0
        self.x = x*TILESIZE
        self.y = y*TILESIZE
        self.rect.x = self.x
        self.rect.y = self.y

class floor2(Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        Sprite.__init__(self, self.groups)
        self.game = game
        #copied code from the mob
        self.image = pg.image.load(path.join(self.game.img_dir, "grass.png")).convert()
        self.image = self.image.subsurface((0, 32, 32, 32))
        self.rect = self.image.get_rect()
        self.vx, self.vy = 0,0
        self.x = x*TILESIZE
        self.y = y*TILESIZE
        self.rect.x = self.x
        self.rect.y = self.y

#copied wall, but changed color has no collision detection and is just the lake
class Lake(Sprite):
    def __init__(self, game, x, y):
        #allows the player to actually detect the lake
        self.groups = game.all_sprites, game.all_lakes
        Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.vx, self.vy = 0,0
        self.x = x*TILESIZE
        self.y = y*TILESIZE
        self.rect.x = self.x
        self.rect.y = self.y

#Copied base for merchant from wall and lake and floor for the sprite to show up

class Merchant(Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.all_merchants
        Sprite.__init__(self, self.groups)
        self.game = game
        #new code from chatgpt asking to help make the backround of the sprite into the same color
        self.image = pg.image.load(path.join(self.game.img_dir, "merchant.png")).convert_alpha()
        self.image = self.image.subsurface((0, 0, 32, 32))
        self.rect = self.image.get_rect()
        self.vx, self.vy = 0,0
        self.x = x*TILESIZE
        self.y = y*TILESIZE
        self.rect.x = self.x
        self.rect.y = self.y


# got the code from wall just changed how it looks like, and also made it have collision detection
class house(Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.all_walls
        Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.fill(BROWN)
        self.rect = self.image.get_rect()
        self.vx, self.vy = 0,0
        self.x = x*TILESIZE
        self.y = y*TILESIZE
        self.rect.x = self.x
        self.rect.y = self.y

#added fish class which is the main part of the game and made it have special effects from random and chances from 1-100
class Fish:
    def __init__(self):
        #determining the rarity of the fish based on a random number between 1 and 100
        number = randint(1, 1000)
        type = randint(1, 5)

        if number <= 100:
            self.rarity = "common"
            if type == 1:
                self.name = "Salmon"
            if type == 2:
                self.name = "Trout"
            if type == 3:
                self.name = "Bass"
            if type == 4:
                self.name = "Catfish"
            if type == 5:
                self.name = "Pike"
        elif number <= 800:
            self.rarity = "uncommon"
            if type == 1:
                self.name = "Rainbow Trout"
            if type == 2:
                self.name = "Walleye"
            if type == 3:
                self.name = "Perch"
            if type == 4:
                self.name = "Bluegill"
            if type == 5:
                self.name = "Crappie"
        elif number <= 950:
            self.rarity = "rare"
            if type == 1:
                self.name = "Sturgeon"
            if type == 2:
                self.name = "Muskellunge"
            if type == 3:
                self.name = "Jellyfish"
            if type == 4:
                self.name = "Eel"
            if type == 5:
                self.name = "Swordfish"
        elif number == 1000:
            self.rarity = "impossible"
            if type == 1:
                self.name = "Mermaid"
            if type == 2:
                self.name = "Sea Serpent"
            if type == 3:
                self.name = "Alien???"
            if type == 4:
                self.name = "Godzilla???"
            if type == 5:
                self.name = "Fisherman???"
        else:
            self.rarity = "legendary"
            if type == 1:
                self.name = "Golden Trout"
            if type == 2:
                self.name = "Fish with gun"
            if type == 3:
                self.name = "Shark"
            if type == 4:
                self.name = "Whale"
            if type == 5:
                self.name = "Kraken"

        self.weight = randint(1, 10)

        # base attack based on rarity
        if self.rarity == "common":
            base_attack = 10
        elif self.rarity == "uncommon":
            base_attack = 20
        elif self.rarity == "rare":
            base_attack = 35
        elif self.rarity == "legendary":
            base_attack = 50
        elif self.rarity == "impossible":
            base_attack = 100

        # base health based on rarity
        if self.rarity == "common":
            base_health = 100
        elif self.rarity == "uncommon":
            base_health = 200
        elif self.rarity == "rare":
            base_health = 350
        elif self.rarity == "legendary":
            base_health = 500
        elif self.rarity == "impossible":
            base_health = 1000

        self.health = base_health

        # storing the maximum health for healing and catching calculations
        self.max_health = base_health

        # experience and leveling
        self.level = 1
        self.xp = 0
        self.xp_to_next_level = 100

        # evolution information
        self.evolution_stage = 0
        self.evolutions = []


        #got this code from chatgpt to make the attack of the fish have a random variation of -20% to +20% of the base attack
        variation = randint(-20, 20)
        self.attack = int(base_attack * (1 + variation / 100))

        effects = ["glowing", "poisonous", "electric", "frozen", "fiery", "radioactive", "mutated", "invisible", "ugly", "mogging", "agressive", "weird", "strong"]

        special = randint(1, 1000)

        if special <= 100:
            self.traits = effects[randint(0, len(effects) - 1)]
        elif special == 1000:
            self.traits = "One shot"
        else:
            self.traits = "none"

        self.crit_chance = 1

    def deal_damage(self):
        damage = self.attack

        if randint(1, 100) == self.crit_chance:
            damage = int(damage * 1.5)
            print("CRITICAL HIT!")

        return damage
    # giving the fish experience and leveling it up
    def gain_xp(self, amount):
        self.xp += amount

        while self.xp >= self.xp_to_next_level:
            self.xp -= self.xp_to_next_level
            self.level += 1

            # increasing fish stats when leveling up
            self.max_health = int(self.max_health * 1.1)
            self.attack += 2
            self.health = self.max_health

            # increasing the amount of xp needed for the next level
            self.xp_to_next_level = int(self.xp_to_next_level * 1.25)

            print(self.name, "reached level", self.level, "!")

#added the attacks for the fish
#I had to individually make each one and it took a while
#also name them and each have different damage and accuracy based on the rarity of the fish and type of fish

class Attack_1:
    def __init__(self, fish):
        attacks = {
            "Salmon": ("Salmon Bite", 10, 90),
            "Trout": ("Trout Tail", 15, 85),
            "Bass": ("Bass Slam", 20, 80),
            "Catfish": ("Catfish Whip", 25, 75),
            "Pike": ("Pike Strike", 30, 70),

            "Rainbow Trout": ("Rainbow Tail", 20, 90),
            "Walleye": ("Walleye Bite", 25, 85),
            "Perch": ("Perch Slam", 30, 80),
            "Bluegill": ("Bluegill Whip", 35, 75),
            "Crappie": ("Crappie Strike", 40, 70),

            "Sturgeon": ("Sturgeon Tail", 30, 90),
            "Muskellunge": ("Muskellunge Bite", 35, 85),
            "Jellyfish": ("Jellyfish Slam", 40, 80),
            "Eel": ("Eel Whip", 45, 75),
            "Swordfish": ("Swordfish Strike", 50, 70),

            "Golden Trout": ("Money", 50, 90),
            "Fish with gun": ("Shoot", 55, 85),
            "Shark": ("Shark Bite", 60, 80),
            "Whale": ("Whale Slam", 65, 75),
            "Kraken": ("Kraken Strike", 70, 70),

            "Mermaid": ("Mermaid Sing", 100, 90),
            "Sea Serpent": ("Sea Serpent Bite", 105, 85),
            "Alien": ("Alien Laser", 110, 80),
            "Godzilla": ("Godzilla Breath", 115, 75),
            "Fisherman": ("Fisherman Hook", 120, 70)
        }

        self.name, self.damage, self.accuracy = attacks.get(
            fish.name, ("Basic Bite", 10, 90)
        )


class Attack_2:
    def __init__(self, fish):
        attacks = {
            "Salmon": ("River Splash", 15, 85),
            "Trout": ("Rapid Current", 20, 80),
            "Bass": ("Headbutt", 25, 75),
            "Catfish": ("Whisker Hit", 30, 70),
            "Pike": ("Lunge", 35, 65),

            "Rainbow Trout": ("Rainbow Wave", 25, 85),
            "Walleye": ("Big Hit", 30, 80),
            "Perch": ("School Swarm", 35, 75),
            "Bluegill": ("Fin Hit", 40, 70),
            "Crappie": ("Water Burst", 45, 65),

            "Sturgeon": ("Sturgeon Charge", 35, 85),
            "Muskellunge": ("Eat and Bite", 40, 80),
            "Jellyfish": ("Electric Shock", 45, 75),
            "Eel": ("Lightning Shock", 50, 70),
            "Swordfish": ("Pierce", 55, 65),

            "Golden Trout": ("Golden Fortune", 60, 85),
            "Fish with gun": ("Double Shot", 65, 80),
            "Shark": ("Hungy Hungry Sharkie", 70, 75),
            "Whale": ("Big Bellyflop", 75, 70),
            "Kraken": ("Tentacle Crush", 80, 65),

            "Mermaid": ("Siren's Bad Song", 110, 85),
            "Sea Serpent": ("Big Chomp", 115, 80),
            "Alien": ("Blow up", 120, 75),
            "Godzilla": ("Big stomp", 125, 70),
            "Fisherman": ("Fishing Boat", 130, 65)
        }

        self.name, self.damage, self.accuracy = attacks.get(
            fish.name, ("Basic Splash", 15, 85)
        )


class Attack_3:
    def __init__(self, fish):
        attacks = {
            "Salmon": ("Upstream", 25, 70),
            "Trout": ("Crash Into", 30, 65),
            "Bass": ("Play the Base", 35, 60),
            "Catfish": ("Mudslide", 40, 55),
            "Pike": ("Pike Spike", 45, 50),

            "Rainbow Trout": ("Rain Bow", 35, 70),
            "Walleye": ("Wall and an Eye", 40, 65),
            "Perch": ("Fin", 45, 60),
            "Bluegill": ("Blue Burst", 50, 55),
            "Crappie": ("Really unusual Bite", 55, 50),

            "Sturgeon": ("Perform Surgery", 45, 70),
            "Muskellunge": ("Far Lunge", 50, 65),
            "Jellyfish": ("Electric Eel", 55, 60),
            "Eel": ("Electric Jellyfish", 60, 55),
            "Swordfish": ("Ultimate Piercing", 65, 50),

            "Golden Trout": ("Midas Touch", 70, 70),
            "Fish with gun": ("Big shot", 75, 65),
            "Shark": ("Jaws???", 80, 60),
            "Whale": ("Eat the Fish", 85, 55),
            "Kraken": ("Headbutt", 90, 50),

            "Mermaid": ("A really good song", 120, 70),
            "Sea Serpent": ("Eat itself", 125, 65),
            "Alien": ("A really big big bomb", 130, 60),
            "Godzilla": ("Fire a Missile", 135, 55),
            "Fisherman": ("Catch the Fish", 140, 50)
        }

        self.name, self.damage, self.accuracy = attacks.get(
            fish.name, ("Basic Crush", 25, 70)
        )


class Special_Attack:
    def __init__(self, name, damage, accuracy):
        if self.fish.trait == "glowing":
            self.name = "Glowing Strike"
            self.fish.attack_1 += randint(10, 30)
            self.accuracy = 80
        if self.fish.trait == "poisonous":
            self.name = "Poisonous Strike"
            self.fish.attack_1 += randint(10, 30)
            self.accuracy = 70
        if self.fish.trait == "electric":
            self.name = "Electric Strike"
            self.fish.attack_1 += randint(10, 30)
            self.accuracy = 75
        if self.fish.trait == "frozen":
            self.name = "Frozen Strike"
            self.fish.attack_1 += randint(15, 30)
            self.accuracy = 85
        if self.fish.trait == "fiery":
            self.name = "Fiery Strike"
            self.fish.attack_1 += randint(25, 45)
            self.accuracy = 65
        if self.fish.trait == "radioactive":
            self.name = "Radioactive Strike"
            self.fish.attack_1 += randint(30, 50)
            self.accuracy = 60
        if self.fish.trait == "mutated":
            self.name = "Mutated Strike"
            self.fish.attack_1 += randint(40, 60)
            self.accuracy = 55
        if self.fish.trait == "invisible":
            self.name = "Invisible Strike"
            self.fish.attack_1 += randint(5, 15)
            self.accuracy = 90
        if self.fish.trait == "ugly":
            self.name = "Ugly Strike"
            self.fish.attack_1 += randint(1, 10)
            self.accuracy = 95
        if self.fish.trait == "mogging":
            self.name = "Mogging Strike"
            self.fish.attack_1 += randint(40, 50)
            self.accuracy = 50
        if self.fish.trait == "agressive":
            self.name = "Agressive Strike"
            self.fish.attack_1 += randint(10, 30)
            self.accuracy = 80
        if self.fish.trait == "weird":
            self.name = "Weird Strike"
            self.fish.attack_1 += randint(20, 40)
            self.accuracy = 70
        if self.fish.trait == "strong":
            self.name = "Strong Strike"
            self.fish.attack_1 += randint(30, 50)
            self.accuracy = 60

class Item:
    def __init__(self, name, effect):
        pass


# creating a net that can be used to catch fish
# basically the pokeball in pokemmon
class Net:
    def __init__(self, name="Basic Net", uses=10):
        self.name = name
        self.uses = uses

    # using one net attempt
    def use(self):
        if self.uses <= 0:
            print("Your net is broken!")
            return False

        self.uses -= 1
        return True


#another class to add a battle, basically a pokemon style battle system where the player can attack, special attack, use item, swap fish, and enemy turn
#got majority of code from ChatGPT and then modified it as well as used a bunch of code I got myself
class Battle:
    def __init__(self, player, enemy, fish_collection=None, net=None):
        # the two main entities for the battle
        self.player = player
        self.enemy = enemy

        self.fish_collection = fish_collection if fish_collection else [player]

        #first turn is the player turn, then enemy turn, then player turn, then enemy turn, etc
        self.turn = 0
        self.special_ready = False
        self.swap_used = False
        self.battle_over = False

        # Creating the player's attacks
        self.player_attacks = [
            Attack_1(player),
            Attack_2(player),
            Attack_3(player)
        ]

        # Creating the enemy's attacks
        self.enemy_attacks = [
            Attack_1(enemy),
            Attack_2(enemy),
            Attack_3(enemy)
        ]

        # Items
        self.potions = 3

        # using a net bought from the merchant when one is provided
        self.net = net if net else Net()

    # Counting player turns
    def next_turn(self):
        self.turn += 1
        #getting ready for the special attack every 3 turns
        if self.turn % 3 == 0:
            self.special_ready = True
            print("SPECIAL ATTACK READY!")

    # Checking whether the battle has ended
    def check_battle(self):
        if self.enemy.health <= 0:
            self.enemy.health = 0
            self.battle_over = True
            print(self.enemy.name, "has been defeated!")
            print("YOU WON!")
        #checking if the player has fainted and if they have another fish to swap to, if not then the player loses
        elif self.player.health <= 0:
            self.player.health = 0
            self.battle_over = True
            print(self.player.name, "has fainted!")

            # Check if another fish is available
            available = [
                fish for fish in self.fish_collection
                if fish.health > 0 and fish != self.player
            ]

            if available:
                #choosing anotehr fish to swap to if the player has another fish
                print("Choose another fish!")
            else:
                #lost the game if the player has no more fish to swap to
                print("YOU LOST!")

        return self.battle_over

    # Calculating damage
    def calculate_damage(self, attack, attacker):

        if randint(1, 100) > attack.accuracy:
            print("The attack missed!")
            return 0

        damage = attack.damage

        # Critical hit
        if randint(1, 100) == attacker.crit_chance:
            damage = int(damage * 1.5)
            print("CRITICAL HIT!")

        return damage

    # Player regular attack
    def attack(self, attack_number):
        if self.battle_over:
            return

        if attack_number < 1 or attack_number > 3:
            print("Invalid attack!")
            return

        attack = self.player_attacks[attack_number - 1]

        print(self.player.name, "used", attack.name)

        damage = self.calculate_damage(attack, self.player)

        self.enemy.health -= damage

        print("Damage:", damage)
        print("Enemy health:", max(0, self.enemy.health))

        self.next_turn()
        self.check_battle()

        if not self.battle_over:
            self.enemy_turn()

    # Special attack
    def special_attack(self):
        if self.battle_over:
            return

        if not self.special_ready:
            print("Special attack is not ready!")
            return

        self.special_ready = False

        print(self.player.name, "used its SPECIAL ATTACK!")

        # One Shot trait
        if self.player.traits == "One shot":
            damage = 1000000
            print("ONE SHOT!")

        else:
            # Regular special attack damage
            damage = int(self.player.attack * 3)

        self.enemy.health -= damage

        print("Special damage:", damage)
        print("Enemy health:", max(0, self.enemy.health))

        self.check_battle()

        if not self.battle_over:
            self.enemy_turn()

    # Using items
    def use_item(self):
        if self.battle_over:
            return

        if self.potions <= 0:
            print("You have no potions!")
            return

        if self.player.health >= self.player.max_health:
            print("Your fish does not need healing!")
            return

        self.potions -= 1

        self.player.health += 50

        if self.player.health > self.player.max_health:
            self.player.health = self.player.max_health

        print("Used a potion!")
        print("Your health:", self.player.health)
        print("Potions left:", self.potions)

        self.next_turn()
        self.enemy_turn()

    # Swapping fish
    def swap(self, fish):
        if self.battle_over:
            return

        if self.swap_used:
            print("You already swapped this battle!")
            return

        if fish not in self.fish_collection:
            print("You do not own this fish!")
            return

        if fish.health <= 0:
            print("This fish has fainted!")
            return

        if fish == self.player:
            print("This fish is already battling!")
            return

        self.player = fish

        self.player_attacks = [
            Attack_1(fish),
            Attack_2(fish),
            Attack_3(fish)
        ]

        self.swap_used = True

        print("Swapped to", fish.name)

        self.next_turn()
        self.enemy_turn()

    def catch_fish(self):
        if self.battle_over:
            return

        catch_chance = 50  # Base catch chance

        # Modify catch chance based on enemy rarity
        if self.enemy.rarity == "common":
            catch_chance += 20
        elif self.enemy.rarity == "uncommon":
            catch_chance += 10
        elif self.enemy.rarity == "rare":
            catch_chance -= 10
        elif self.enemy.rarity == "legendary":
            catch_chance -= 20
        elif self.enemy.rarity == "impossible":
            catch_chance -= 30

        # the fish must be below 10 percent health before it can be caught
        if self.enemy.health < self.enemy.max_health * 0.1:

            # using one net only when the fish is weak enough to catch
            if not self.net.use():
                return

            if randint(1, 100) <= catch_chance:
                print("You caught the", self.enemy.name + "!")
                self.fish_collection.append(self.enemy)
                self.battle_over = True
            else:
                print("The", self.enemy.name, "escaped!")
                self.next_turn()
                self.enemy_turn()
        else:
            print("The fish is too strong to catch! Lower its health first.")
            self.next_turn()
            self.enemy_turn()

    # Enemy turn
    def enemy_turn(self):
        if self.battle_over:
            return

        # Randomly choosing one of the enemy's attacks
        attack = self.enemy_attacks[randint(0, 2)]

        print(self.enemy.name, "used", attack.name)

        damage = self.calculate_damage(attack, self.enemy)

        self.player.health -= damage

        print("Damage taken:", damage)
        print("Your health:", max(0, self.player.health))

        self.check_battle()


#making mob
class Mob(Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.all_mobs
        Sprite.__init__(self, self.groups)
        self.game = game
        #loading from the spritesheet and adding in mob
        self.spritesheet = Spritesheet(path.join(self.game.img_dir, "sprite_sheet.png"))
        self.load_images()
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image = self.spritesheet.get_image(0,0,TILESIZE, TILESIZE)
        # self.image.fill(RED)
        self.rect = self.image.get_rect()
        #speed for mob
        self.speed = 80
        self.vel = vec(0,0)
        self.pos = vec(x*TILESIZE,y*TILESIZE)
        self.x = x*TILESIZE
        self.y = y*TILESIZE
        self.rect.x = self.x
        self.rect.y = self.y
        self.dir = "none"
        self.last_update = 0
        self.current_frame = 0
        self.hit_rect = MOB_HIT_RECT
        #debugging to see for mob and if it spawns or not
        print("mob initialized")
        print(self.rect.x)
        print(self.rect.y)
    #mob animation and movement
    def load_images(self):
            self.idle_frames = [self.spritesheet.get_image(64,0,TILESIZE, TILESIZE),
                                self.spritesheet.get_image(96,0,TILESIZE, TILESIZE)
                                ]
            self.run_frames = [self.spritesheet.get_image(0,0,TILESIZE, TILESIZE),
                                self.spritesheet.get_image(TILESIZE,0,TILESIZE, TILESIZE)
                                ]    
    #animation for mob
    def animate(self):
            # use the time element to get now
            now = pg.time.get_ticks()
            if self.dir == "none":
                if now - self.last_update > 350:
                    self.last_update = now
                    self.current_frame = (self.current_frame + 1) % len(self.idle_frames)
                    bottom = self.rect.bottom
                    self.image = self.idle_frames[self.current_frame]
                    self.image.set_colorkey(BLACK)
                    self.rect = self.image.get_rect()
                    self.rect.bottom = bottom
            elif self.dir == "right":
                pass

    # uses autocpomplete to fill in the rest of the code for the update method
    #chasing the player with the mob
    def chase(self, obj):
        if self.pos.x < obj.pos.x:
            self.vel.x = self.speed
            self.dir = "right"
        elif self.pos.x > obj.pos.x:
            self.vel.x = -self.speed
            self.dir = "left"
        else:
            self.vel.x = 0

        if self.pos.y < obj.pos.y:
            self.vel.y = self.speed
        elif self.pos.y > obj.pos.y:
            self.vel.y = -self.speed
        else:
            self.vel.y = 0

    def update(self):
        self.animate()

        self.chase(self.game.player)
        self.rect.center = self.pos
        self.pos += self.vel * self.game.dt
        self.hit_rect.centerx = self.pos.x
        collide_with_walls(self, self.game.all_walls, 'x')
        self.hit_rect.centery = self.pos.y
        collide_with_walls(self, self.game.all_walls, 'y')
        self.rect.center = self.hit_rect.center