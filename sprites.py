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
        if keys[pg.K_LEFT] or keys[pg.K_a]:
            self.acc.x = -PLAYER_SPEED
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            self.dir = "right"
            self.acc.x = PLAYER_SPEED
        if keys[pg.K_UP] or keys[pg.K_w]:
            self.acc.y = -PLAYER_SPEED
        if keys[pg.K_LEFT] or keys[pg.K_s]:
            self.acc.y = PLAYER_SPEED
        # check to see if player is moving diagonaly
        if keys[pg.K_SPACE]:
            self.jump()
        if self.vel.x != 0 and self.vel.y != 0:
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
        self.acc = vec(0,PLAYER_GRAV)
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
                p = Particle(self.game, hits[0].pos.x, hits[0].pos.y)
            self.coins += 1
            self.game.pickup_snd.play()
            self.game.score += 1
        self.hit_rect.centerx = self.pos.x
        collide_with_walls(self, self.game.all_walls, 'x')
        self.hit_rect.centery = self.pos.y
        if collide_with_walls(self, self.game.all_walls, 'y'):
            self.jumping = False
        self.rect.center = self.hit_rect.center

    
# making class wall, coin, and mob
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

class Coin(Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.all_coins
        Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((TILESIZE, TILESIZE))
        pg.draw.circle(self.image, YELLOW, (TILESIZE//2, TILESIZE//2), TILESIZE//2)
        self.rect = self.image.get_rect()
        self.vx, self.vy = 0,0
        self.x = x*TILESIZE
        self.y = y*TILESIZE
        self.rect.x = self.x
        self.rect.y = self.y

class Particle(Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.all_particles
        Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((5, 5))
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


        
class Mob(Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.all_mobs
        Sprite.__init__(self, self.groups)
        self.game = game
        self.spritesheet = Spritesheet(path.join(self.game.img_dir, "sprite_sheet.png"))
        self.load_images()
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image = self.spritesheet.get_image(0,0,TILESIZE, TILESIZE)
        # self.image.fill(RED)
        self.rect = self.image.get_rect()
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
        