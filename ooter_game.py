from pygame import *
from random import randint
from pygame import time

# Инициализация
# mixer.init()
# mixer.music.load('space.ogg')
# mixer.music.play()
# fire_sound = mixer.Sound('fire.ogg')

font.init()
font1 = font.SysFont("Arial", 36)
font2 = font.SysFont("Arial", 36)
win = font1.render('YOU WIN!', True, (255, 255, 255))
lose = font1.render('YOU LOSE!', True, (180, 0, 0))

img_back = "galaxy.jpg"
img_hero = "rocket.png"
img_enemy = "ufo.png"
img_bullet = 'bullet.png'
img_aster = 'asteroid.png'
img_shield = 'shield_bottle.png'  

score = 0 
lost = 0
max_lost = 10
goal = 300

# ВРАГИ для волн
enemies_in_wave = 6
enemies_per_wave_increment = 2
wave = 1
max_waves = 5
enemies_destroyed_in_wave = 0  # счётчик уничтоженных врагов в текущей волне

# Определение функций
def spawn_enemies(count):
    for i in range(count):
        monster = Enemy(img_enemy, randint(80, win_width - 80), -40, 80, 50, randint(1, 5))
        monsters.add(monster)

# Классы
class GameSprite(sprite.Sprite):
    def __init__(self, player_image, player_x, player_y, size_x, size_y, player_speed):
        sprite.Sprite.__init__(self)
        self.image = transform.scale(image.load(player_image), (size_x, size_y))
        self.speed = player_speed
        self.rect = self.image.get_rect()
        self.rect.x = player_x
        self.rect.y = player_y
    def reset(self):
        window.blit(self.image, (self.rect.x, self.rect.y))

class Player(GameSprite):
    def update(self):
        keys = key.get_pressed()
        if keys[K_LEFT] and self.rect.x > 5:
            self.rect.x -= self.speed
        if keys[K_RIGHT] and self.rect.x < win_width - 80:
            self.rect.x += self.speed
    def fire(self):
        bullet = Bullet(img_bullet, self.rect.centerx-9, self.rect.top, 15, 20, -15)
        bullets.add(bullet)

class Enemy(GameSprite):
    def update(self):
        self.rect.y += self.speed
        global lost
        if self.rect.y > win_height:
            self.rect.x = randint(80, win_width - 80)
            self.rect.y = 0
            lost += 1

class Bullet(GameSprite):
    def update(self):
        self.rect.y += self.speed
        if self.rect.y < 0:
            self.kill()

class Fon(GameSprite):
    def update(self):
        self.rect.y += self.speed
        global lost
        if self.rect.y > win_height:
            self.rect.x = randint(80, win_width - 80)
            self.rect.y = 0

class ShieldBottle(GameSprite):
    def update(self):
        self.rect.y += self.speed
        if self.rect.y > win_height:
            self.rect.x = randint(80, win_width - 80)
            self.rect.y = 0

# Настройка окна
win_width = 700
win_height= 500
display.set_caption("Shooter")
window = display.set_mode((win_width, win_height))
background = transform.scale(image.load(img_back), (win_width, win_height))

# Создаём игрока
ship = Player(img_hero, win_width/2+40, win_height - 100, 80, 100, 10)

# Создание групп врагов, пуль, астероидов и бутылей
monsters = sprite.Group()
spawn_enemies(enemies_in_wave)

bullets = sprite.Group()

aster = sprite.Group()
for i in range(8):
    asteroid = Fon(img_enemy, randint(20, win_width - 20), randint(20, win_height - 20), 20, 50, 0)
    aster.add(asteroid)

shield_bottles = sprite.Group()
for i in range(2):
    bottle = ShieldBottle(img_shield, randint(80, win_width - 80), randint(-150, -40), 40, 60, randint(1, 3))
    shield_bottles.add(bottle)

# Варианты состояния
finish = False
run = True

shield_active = False
shield_start_time = 0

# Переменные для волн
enemies_in_wave_current = enemies_in_wave
enemies_destroyed_in_wave = 0

def start_new_wave():
    global enemies_in_wave_current, enemies_destroyed_in_wave, wave
    wave += 1
    enemies_in_wave_current += enemies_per_wave_increment
    spawn_enemies(enemies_in_wave_current)
    enemies_destroyed_in_wave = 0

# Основной цикл
while run:
    for e in event.get():
        if e.type == QUIT:
            run = False
        if e.type == KEYDOWN:
            if e.key == K_ESCAPE:
                run = False
            if e.key == K_SPACE:
                #fire_sound.play()
                ship.fire()

    if not finish:
        window.blit(background, (0,0))
        # Отображение счёта и пропущенных
        text = font2.render("Счет:" + str(score), 1, (255, 255, 255))
        window.blit(text, (10, 20))
        text_lose = font2.render("Пропущено:" + str(lost), 1, (255, 255, 255))
        window.blit(text_lose, (10, 50))
        # Отображение этапа
        stage_text = font2.render(f"Этап ({wave})", True, (255, 255, 255))
        window.blit(stage_text, (10, 80))
        
        # Обновление спрайтов
        ship.update()
        monsters.update()
        bullets.update()
        shield_bottles.update()

        # Коллизии пуль и врагов
        collides = sprite.groupcollide(monsters, bullets, True, True)
        for c in collides:
            score += 1
            enemies_destroyed_in_wave += 1
            monster = Enemy(img_enemy, randint(80, win_width-80), -40, 80, 50, randint(1, 5))
            monsters.add(monster)

        # Проверка проигрыша
        if sprite.spritecollide(ship, monsters, False) and not shield_active or lost >= max_lost:
            finish = True
            window.blit(lose, (200, 200))
        # Проверка победы
        if score >= goal:
            finish = True
            window.blit(win, (200, 200))
        # Проверка окончания волны
        if len(monsters) == 0:
            if wave >= max_waves:
                # Победа по окончания волн
                finish = True
                window.blit(win, (200, 200))
            else:
                start_new_wave()
                # Небольшая задержка перед следующей волной
                time.delay(2000)
        
        # Отрисовка и управление щитом
        ship.reset()
        monsters.draw(window)
        bullets.draw(window)
        aster.draw(window)
        shield_bottles.draw(window)

        # Обработка щита
        shield_hits = sprite.spritecollide(ship, shield_bottles, True)
        if shield_hits:
            shield_active = True
            shield_start_time = time.get_ticks()

        if shield_active:
            current_time = time.get_ticks()
            if current_time - shield_start_time <= 5000:
                draw.circle(window, (0, 255, 255), (ship.rect.centerx, ship.rect.centery), 50, 3)
            else:
                shield_active = False

        display.update()

        # Проверка, если убийств достигнуто 10, начинаем следующую волну
        if enemies_destroyed_in_wave >= 35:
            if wave >= max_waves:
                finish = True
                window.blit(win, (200, 200))
            else:
                start_new_wave()
                time.delay(2000)
    else:
        # После окончания уровня или проигрыша
        for b in bullets:
            b.kill()
        for m in monsters:
            m.kill()
        for s in shield_bottles:
            s.kill()
        for a in aster:
            a.kill()

        # Можно добавить рестарт или выход
        # Например, возвращаемся к первой волне или завершаем игру
        # Для простоты оставим так

    time.delay(50)