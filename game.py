import pygame
import math
import random
from pygame.math import Vector3
#im gay)))
pygame.init()

WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("game test (LOW FPS,TEXTURE)")

wall_texture = pygame.image.load('bricksx64.png')
weapon_texture = pygame.image.load('gun.png')
muzzle_flash = pygame.image.load('muzzle.png')
enemy_texture = pygame.image.load('enemy.png')

wall_texture = pygame.transform.scale(wall_texture, (64, 64))

player_pos = Vector3(1.5, 1.5, 0)
player_angle = 0
player_speed = 0.05

MAP_SIZE = 32

weapon_cooldown = 0
WEAPON_COOLDOWN_MAX = 20
muzzle_flash_time = 0

map_data = None
bullets = []
enemies = []

def generate_map():
    map_data = [[1 for _ in range(MAP_SIZE)] for _ in range(MAP_SIZE)]
    rooms = []
    
    for _ in range(10):
        room_width = random.randint(4, 8)
        room_height = random.randint(4, 8)
        x = random.randint(1, MAP_SIZE - room_width - 1)
        y = random.randint(1, MAP_SIZE - room_height - 1)
        
        if not any(x < r[0] + r[2] and x + room_width > r[0] and y < r[1] + r[3] and y + room_height > r[1] for r in rooms):
            for i in range(y, y + room_height):
                for j in range(x, x + room_width):
                    map_data[i][j] = 0
            rooms.append((x, y, room_width, room_height))
    
    for i in range(len(rooms) - 1):
        x1, y1 = rooms[i][0] + rooms[i][2] // 2, rooms[i][1] + rooms[i][3] // 2
        x2, y2 = rooms[i+1][0] + rooms[i+1][2] // 2, rooms[i+1][1] + rooms[i+1][3] // 2
        
        while x1 != x2 or y1 != y2:
            if x1 < x2:
                x1 += 1
            elif x1 > x2:
                x1 -= 1
            elif y1 < y2:
                y1 += 1
            elif y1 > y2:
                y1 -= 1
            map_data[y1][x1] = 0
    
    start_room = random.choice(rooms)
    player_pos.x = start_room[0] + start_room[2] // 2 + 0.5
    player_pos.y = start_room[1] + start_room[3] // 2 + 0.5
    
    return map_data

map_data = generate_map()

def spawn_enemies(num_enemies):
    for _ in range(num_enemies):
        while True:
            x = random.randint(0, MAP_SIZE - 1)
            y = random.randint(0, MAP_SIZE - 1)
            if map_data[y][x] == 0:
                enemies.append({'pos': Vector3(x + 0.5, y + 0.5, 0), 'health': 100})
                break

def draw_3d_scene():
    for x in range(0, WIDTH):
        ray_angle = (player_angle - 30 + (60 * x / WIDTH)) * math.pi / 180
        
        ray_x = player_pos.x
        ray_y = player_pos.y
        
        sin_a = math.sin(ray_angle)
        cos_a = math.cos(ray_angle)
        
        wall_hit = False
        distance = 0
        wall_height = HEIGHT

        while not wall_hit and distance < 20:
            distance += 0.01
            ray_x = player_pos.x + distance * cos_a
            ray_y = player_pos.y + distance * sin_a
            
            map_x = int(ray_x)
            map_y = int(ray_y)
            
            if map_data[map_y][map_x] == 1:
                wall_hit = True
        
        if wall_hit:
            wall_height = min(int(HEIGHT / (distance * math.cos((ray_angle - player_angle * math.pi / 180)))), HEIGHT)
            
            if abs(sin_a) > abs(cos_a):
                tex_x = int((ray_x % 1) * 64)
            else:
                tex_x = int((ray_y % 1) * 64)
            
            if (sin_a > 0 and cos_a <= 0) or (sin_a <= 0 and cos_a < 0):
                tex_x = 63 - tex_x
            
            wall_column = wall_texture.subsurface((tex_x, 0, 1, 64))
            wall_column = pygame.transform.scale(wall_column, (1, wall_height))
            
            start_y = (HEIGHT - wall_height) // 2
            screen.blit(wall_column, (x, start_y))
            
            shade = min(1, 1 - (distance / 20))
            dark_surface = pygame.Surface((1, wall_height)).convert_alpha()
            dark_surface.fill((0, 0, 0, (1 - shade) * 255))
            screen.blit(dark_surface, (x, start_y))
        
        if wall_height < HEIGHT:
            pygame.draw.line(screen, (100, 100, 100), (x, 0), (x, (HEIGHT - wall_height) // 2))
            pygame.draw.line(screen, (50, 50, 50), (x, (HEIGHT + wall_height) // 2), (x, HEIGHT))

    for enemy in enemies:
        dx = enemy['pos'].x - player_pos.x
        dy = enemy['pos'].y - player_pos.y
        dist = math.sqrt(dx*dx + dy*dy)
        enemy_angle = math.atan2(dy, dx) - player_angle * math.pi / 180
        
        if -math.pi/2 < enemy_angle < math.pi/2:
            enemy_height = min(int(HEIGHT / dist), HEIGHT)
            enemy_width = enemy_height // 2
            enemy_x = int(WIDTH/2 + math.tan(enemy_angle) * WIDTH/2) - enemy_width // 2
            enemy_y = HEIGHT // 2 - enemy_height // 2
            
            enemy_sprite = pygame.transform.scale(enemy_texture, (enemy_width, enemy_height))
            screen.blit(enemy_sprite, (enemy_x, enemy_y))

def draw_weapon():
    weapon_size = 200
    weapon_pos = (WIDTH // 2 - weapon_size // 2, HEIGHT - weapon_size)
    weapon_texture_scaled = pygame.transform.scale(weapon_texture, (weapon_size, weapon_size))
    screen.blit(weapon_texture_scaled, weapon_pos)
    
    if muzzle_flash_time > 0:
        flash_size = 100
        flash_pos = (WIDTH // 2 - flash_size // 2, HEIGHT - weapon_size - flash_size // 2)
        muzzle_flash_scaled = pygame.transform.scale(muzzle_flash, (flash_size, flash_size))
        screen.blit(muzzle_flash_scaled, flash_pos)

def menu():
    menu_font = pygame.font.Font(None, 74)
    title = menu_font.render('game test (LOW FPS,TEXTURE)', True, (255, 255, 255))
    start_text = menu_font.render('Press SPACE to Start', True, (255, 255, 255))
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return True
        
        screen.fill((0, 0, 0))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//3))
        screen.blit(start_text, (WIDTH//2 - start_text.get_width()//2, HEIGHT*2//3))
        pygame.display.flip()

def game_loop():
    global player_pos, player_angle, weapon_cooldown, muzzle_flash_time, map_data, bullets, enemies
    
    running = True
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    map_data = generate_map()
                    enemies.clear()
                    spawn_enemies(5)
    
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player_angle -= 3
        if keys[pygame.K_RIGHT]:
            player_angle += 3
    
        player_angle %= 360
    
        move_x = 0
        move_y = 0
        if keys[pygame.K_UP]:
            move_x += math.cos(player_angle * math.pi / 180) * player_speed
            move_y += math.sin(player_angle * math.pi / 180) * player_speed
        if keys[pygame.K_DOWN]:
            move_x -= math.cos(player_angle * math.pi / 180) * player_speed
            move_y -= math.sin(player_angle * math.pi / 180) * player_speed
    
        new_x = player_pos.x + move_x
        new_y = player_pos.y + move_y
        if (0 <= int(new_x) < MAP_SIZE and 0 <= int(new_y) < MAP_SIZE and
            map_data[int(new_y)][int(new_x)] == 0):
            player_pos.x = new_x
            player_pos.y = new_y
    
        if keys[pygame.K_SPACE] and weapon_cooldown == 0:
            bullets.append((player_pos.x, player_pos.y, player_angle))
            weapon_cooldown = WEAPON_COOLDOWN_MAX
            muzzle_flash_time = 5

        if weapon_cooldown > 0:
            weapon_cooldown -= 1
        
        if muzzle_flash_time > 0:
            muzzle_flash_time -= 1


        bullets = [(x + math.cos(angle * math.pi / 180) * 0.2, 
                    y + math.sin(angle * math.pi / 180) * 0.2, 
                    angle) for x, y, angle in bullets]

        bullets = [(x, y, angle) for x, y, angle in bullets 
                   if 0 <= int(x) < MAP_SIZE and 0 <= int(y) < MAP_SIZE and map_data[int(y)][int(x)] == 0]

        for bullet in bullets[:]:
            for enemy in enemies[:]:
                if math.hypot(bullet[0] - enemy['pos'].x, bullet[1] - enemy['pos'].y) < 0.5:
                    enemy['health'] -= 20
                    if enemy['health'] <= 0:
                        enemies.remove(enemy)
                    bullets.remove(bullet)
                    break

        for enemy in enemies:
            dx = player_pos.x - enemy['pos'].x
            dy = player_pos.y - enemy['pos'].y
            dist = math.hypot(dx, dy)
            if dist > 0.5:
                enemy['pos'].x += dx / dist * 0.02
                enemy['pos'].y += dy / dist * 0.02

        screen.fill((0, 0, 0))
    
        draw_3d_scene()
        draw_weapon()
    
        map_scale = 4
        for y in range(MAP_SIZE):
            for x in range(MAP_SIZE):
                if map_data[y][x] == 1:
                    pygame.draw.rect(screen, (255, 255, 255), (x * map_scale, y * map_scale, map_scale, map_scale))
    
        pygame.draw.circle(screen, (255, 0, 0), (int(player_pos.x * map_scale), int(player_pos.y * map_scale)), 2)
    
        end_x = int(player_pos.x * map_scale + math.cos(player_angle * math.pi / 180) * 5)
        end_y = int(player_pos.y * map_scale + math.sin(player_angle * math.pi / 180) * 5)
        pygame.draw.line(screen, (0, 255, 0), (int(player_pos.x * map_scale), int(player_pos.y * map_scale)), (end_x, end_y), 1)
    
        for bullet in bullets:
            pygame.draw.circle(screen, (255, 255, 0), (int(bullet[0] * map_scale), int(bullet[1] * map_scale)), 1)
        for enemy in enemies:
            pygame.draw.circle(screen, (255, 0, 0), (int(enemy['pos'].x * map_scale), int(enemy['pos'].y * map_scale)), 2)
    
        pygame.display.flip()
    
        clock.tick(60)

    return True

def main():
    global map_data, enemies
    
    if menu():
        map_data = generate_map()
        spawn_enemies(5)
        while game_loop():
            pass
    
    pygame.quit()

if __name__ == "__main__":
    main()