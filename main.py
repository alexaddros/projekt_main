import pygame
import random
import os
import sys
import copy

FPS = 60
pygame.init()
pygame.display.set_caption('YAPG')
screen = pygame.display.set_mode([600, 600])
screen_rect = (0, 0, 600, 600)
time = pygame.time.Clock()
pygame.mixer.music.load('2.mp3')
pygame.mixer.music.play()


def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    image = pygame.image.load(fullname).convert()
    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = image.convert_alpha()
    return image


tile_images = {'wall': load_image('wall.png'), 
               'empty': load_image('floor.png'), 
               'trap': load_image('trap.png', -1)}

player_image = load_image('character_standing_1.png', -1)
character_right_images = [load_image('character_running_1.png', -1), 
                          load_image('character_running_2.png', -1), 
                          load_image('character_running_3.png', -1), 
                          load_image('character_running_4.png', -1), 
                          load_image('character_running_5.png', -1), 
                          load_image('character_running_6.png', -1), 
                          load_image('character_running_7.png', -1), 
                          load_image('character_running_8.png', -1)]

character_left_images = [pygame.transform.flip(image, True, False) for image in character_right_images]
tile_width = tile_height = 16

all_sprites = pygame.sprite.Group()
solid_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
trap_group = pygame.sprite.Group()
bg_group = pygame.sprite.Group()

heart_group = pygame.sprite.Group()
heart = pygame.sprite.Sprite()
heart.image = load_image("6.gif")
heart.rect = heart.image.get_rect()
heart_group.add(heart)
heart.rect.x = 5
heart.rect.y = 20
heart_group.draw(screen)

WIDTH, HEIGHT = 1000, 1000

def load_level(filename):
    filename = "data/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    max_width = max(map(len, level_map))

    return list(map(lambda x: x.ljust(max_width, ' '), level_map))


class Camera:
    def __init__(self):
        self.dx = 0
        self.dy = 0

    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - WIDTH // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - HEIGHT // 2)


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y, n=False):
        global all_sprites
        global solid_group
        global trap_group
        global bg_group
        global heart_group

        if n:
            all_sprites = pygame.sprite.Group()
            solid_group = pygame.sprite.Group()
            trap_group = pygame.sprite.Group()
            bg_group = pygame.sprite.Group()
            heart_group = pygame.sprite.Group()

        if tile_type == 'wall':
            group = solid_group
        elif tile_type == 'trap':
            group = trap_group
        else:
            group = bg_group

        super().__init__(group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y - 16)
        self.state = 10
        self.last_pushed = [1, 1]
        self.health = 600
        
    def set_health(self, change):
        self.health = self.health - change
        number = self.health // 100

        if number < 1:
            terminate(False, True)
            pygame.init()
            pygame.display.set_caption('YAPG')
            pygame.mixer.music.load('2.mp3')
            pygame.mixer.music.play()
            game(True)      
        else:
            heart.image = load_image("%i.gif" % number)

    def state_delta(self, delta):
        self.state += delta

    def move(self, direction, invert_image, count=1):
        if direction == 'up':
            self.rect = self.rect.move(0, -count / 2)
        elif direction == 'down':
            self.rect = self.rect.move(0, count / 2)
        elif direction == 'left':
            self.rect = self.rect.move(-count / 2, 0)
        elif direction == 'right':
            self.rect = self.rect.move(count / 2, 0)

        if invert_image:
            self.state_delta(-2)
        else:
            self.state_delta(2)

    def clone(self):
        return self

    def update(self, last_pushed):
        global trap_group, solid_group, player_group,bg_group, all_sprites
        
        if pygame.sprite.spritecollide(self, trap_group, False):
            self.set_health(2)
        
        if len(last_pushed) > 2:
            del last_pushed[0]

        if last_pushed[0] != last_pushed[1]:
            self.state = 10
        if self.state >= 90:
            self.state = 0
            return
        
        elif self.state <= -90:
            self.state = -10
            return

        if self.state >= 80:
            self.image = character_right_images[7]
        elif self.state >= 70:
            self.image = character_right_images[6]
        elif self.state >= 60:
            self.image = character_right_images[5]
        elif self.state >= 50:
            self.image = character_right_images[4]
        elif self.state >= 40:
            self.image = character_right_images[3]
        elif self.state >= 30:
            self.image = character_right_images[2]
        elif self.state >= 20:
            self.image = character_right_images[1]
        elif self.state > 0:
            self.image = character_right_images[0]
        elif self.state == 0:
            self.image = player_image

        if self.state <= -80:
            self.image = character_left_images[7]
        elif self.state <= -70:
            self.image = character_left_images[6]
        elif self.state <= -60:
            self.image = character_left_images[5]
        elif self.state <= -50:
            self.image = character_left_images[4]
        elif self.state <= -40:
            self.image = character_left_images[3]
        elif self.state <= -30:
            self.image = character_left_images[2]
        elif self.state <= -20:
            self.image = character_left_images[1]
        elif self.state < 0:
            self.image = character_left_images[0]
        elif self.state == 0:
            self.image = player_image


def generate_level(level, n=False):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y, n)
            elif level[y][x] == '#':
                Tile('wall', x, y, n)
            elif level[y][x] == '@':
                Tile('empty', x, y, n)
                player_xy = (x, y)
            elif level[y][x] == '$':
                Tile('empty', x, y, n)
                Tile('trap', x, y, n)
            n = False
    try:
        new_player = Player(*player_xy)
    except UnboundLocalError:
        new_player = None

    return new_player, x, y



def terminate(n=True, b=False):
    global all_sprites
    global heart_group
    pygame.quit()

    if n:
        sys.exit()
    else:
        pygame.init()

def load_level(filename):
    filename = "data/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    max_width = max(map(len, level_map))

    return list(map(lambda x: x.ljust(max_width, ' '), level_map))


def menu():
    pygame.init()
    pygame.display.set_caption('YAPG')
    screen = pygame.display.set_mode([600, 600])

    time = pygame.time.Clock()
    pygame.mixer.music.load('2.mp3')
    pygame.mixer.music.play()
    
    stop = False
    intro_text = ["Yet Another Pixel Game", "Еще Одна Пиксельная Игра",
                  "Press any button to start", 'Нажми кнопку для старта',
                  "but not power button, please", 'но не кнопку выключения, лол']

    fon = pygame.transform.scale(pygame.image.load('data/logo.jpg'), (600, 600))

    x = -160
    y = 340
    while x < 90:
        z = time.tick()
        x += int(250 * z / 1000)
        y = y - int(250 * z / 1000)
        font = pygame.font.Font("data/pixel.ttf", 38)
        text_coord = 100
        i = 0

        for line in intro_text:
            i += 1
            if i % 2 == 1:
                string_rendered = font.render(line, 10, pygame.Color('blue'))
            else:
                string_rendered = font.render(line, 10, pygame.Color('red'))

            intro_rect = string_rendered.get_rect()
            text_coord += 10
            intro_rect.top = text_coord
            if i % 2 == 1:
                intro_rect.x = x
            else:
                intro_rect.x = y
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    terminate()
                if event.type == pygame.MOUSEBUTTONUP and event.pos[0] > 515 and event.pos[1] > 545:
                    terminate()
                if event.type == pygame.MOUSEBUTTONUP or event.type == pygame.KEYUP:
                    stop = True
            
            if stop:
                break

            text_coord += intro_rect.height
            screen.blit(string_rendered, intro_rect)
            
        pygame.display.update()
        pygame.display.flip()
        screen.blit(fon, (0, 0))
        
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.MOUSEBUTTONUP and event.pos[0] > 515 and event.pos[1] > 545:
                terminate()
            if event.type == pygame.MOUSEBUTTONUP or event.type == pygame.KEYUP:
                stop = True
        if stop:
            break

def game(n=False):
    global o
    global heart_group
    global heart

    menu()
    terminate(False, False)

    pygame.init()
    pygame.display.set_caption('YAPG')
    FPS = 60

    pygame.mixer.music.load('1.mp3')
    pygame.mixer.music.play()

    clock = pygame.time.Clock()
    size = WIDTH, HEIGHT = 1000, 1000
    screen = pygame.display.set_mode(size)
    player, level_x, level_y = generate_level(load_level('level2.txt'), n)

    running = True
    play = True
    back = load_image('back.jpg')
    camera = Camera()

    heart.image = load_image("6.gif")
    heart.rect = heart.image.get_rect()
    heart_group.add(heart)
    heart.rect.x = 5
    heart.rect.y = 20
    heart_group.draw(screen)

    while running:
        o = 1
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()

        if keys[pygame.K_LEFT]:
            flag = True
        else:
            flag = False

        if (keys[pygame.K_UP] or keys[pygame.K_DOWN]) and (keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]):
           o = 0.5
 
        if keys[pygame.K_LEFT]:
            player_from_furute_rect = player.rect
            player_from_furute_rect.x -= 1 * o
            collisions = [True for sprite in solid_group if sprite.rect.colliderect(player.rect)]
            player.last_pushed.append(0)

            if not collisions:
                player.move('left', flag)
            else:
                player.move('right', flag, 2)

        elif keys[pygame.K_RIGHT]:
            player_from_furute_rect = player.rect
            player_from_furute_rect.x += 1 * o
            collisions = [True for sprite in solid_group if sprite.rect.colliderect(player.rect)]
            player.last_pushed.append(1)

            if not collisions:
                player.move('right', flag)
            else:
                player.move('left', flag, 2)

        if keys[pygame.K_DOWN]:
            player_from_furute_rect = player.rect
            player_from_furute_rect.y += 1 * o
            collisions = [True for sprite in solid_group if sprite.rect.colliderect(player.rect)]

            if not collisions:
                player.move('down', flag)
            else:
                player.move('up', flag, 2)

        elif keys[pygame.K_UP]:
            player_from_furute_rect = player.rect
            player_from_furute_rect.y -= 1 * o
            collisions = [True for sprite in solid_group if sprite.rect.colliderect(player.rect)]

            if not collisions:
                player.move('up', flag)
            else:
                player.move('down', flag, 2)
        
        elif keys[pygame.K_1]:
            pygame.mixer.music.set_volume(pygame.mixer.music.get_volume() - 0.1)
            
        elif keys[pygame.K_2]:
            pygame.mixer.music.set_volume(pygame.mixer.music.get_volume() + 0.1)
        
        elif keys[pygame.K_3]:
            if play:
                pygame.mixer.music.pause()
                play = False
            else:
                pygame.mixer.music.unpause()
                play = True
                
        elif keys[pygame.K_LSHIFT]:
            terminate(False, True)
            pygame.init()
            pygame.display.set_caption('YAPG')
            FPS = 60
            pygame.mixer.music.load('2.mp3')
            pygame.mixer.music.play()
            clock = pygame.time.Clock()
            size = WIDTH, HEIGHT = 600, 600
            BLACK = (0, 0, 0)
            screen = pygame.display.set_mode(size)
            back = load_image('back.jpg')
            game(True)    
            
        #heart_group.draw(screen)
        if not any([keys[pygame.K_LEFT], keys[pygame.K_RIGHT], keys[pygame.K_UP], keys[pygame.K_DOWN]]):
            player.state = 0
        
        player.update(player.last_pushed)
        camera.update(player)
        for sprite in all_sprites:
            camera.apply(sprite)
        
        screen.blit(back, (0, 0))

        all_sprites.draw(screen)
        heart_group.draw(screen)
        pygame.display.flip()

        clock.tick(FPS)

game()
