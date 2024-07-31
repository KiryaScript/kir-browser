import pygame
import math
import random
from pygame.math import Vector3

pygame.init()

WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Game Test (LOW FPS)")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

player_pos = Vector3(1.5, 1.5, 0)
player_angle = 0
player_speed = 0.05

MAP_SIZE = 32

def generate_map():
    
    map_data = [[1 for _ in range(MAP_SIZE)] for _ in range(MAP_SIZE)]
    
    x, y = MAP_SIZE // 2, MAP_SIZE // 2
    map_data[y][x] = 0
    
    for _ in range(MAP_SIZE * MAP_SIZE // 3):
        direction = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
        new_x, new_y = x + direction[0], y + direction[1]
        
        if 1 <= new_x < MAP_SIZE - 1 and 1 <= new_y < MAP_SIZE - 1:
            map_data[new_y][new_x] = 0
            x, y = new_x, new_y
    
    player_pos.x = x + 0.5
    player_pos.y = y + 0.5
    
    return map_data

map_data = generate_map()

def draw_3d_scene():
    for x in range(0, WIDTH):
        ray_angle = (player_angle - 30 + (60 * x / WIDTH)) * math.pi / 180
        
        ray_x = player_pos.x
        ray_y = player_pos.y
        
        step_size = 0.01
        dx = math.cos(ray_angle) * step_size
        dy = math.sin(ray_angle) * step_size
        
        wall_hit = False
        distance = 0
        while not wall_hit and distance < 20:
            map_x = int(ray_x)
            map_y = int(ray_y)
            
            if 0 <= map_x < MAP_SIZE and 0 <= map_y < MAP_SIZE:
                if map_data[map_y][map_x] == 1:
                    wall_hit = True
                else:
                    ray_x += dx
                    ray_y += dy
                    distance += step_size
            else:
                wall_hit = True 
        
        if wall_hit:
            cos_angle = math.cos(ray_angle - player_angle * math.pi / 180)
            if abs(cos_angle) < 0.0001 or distance < 0.0001:
                wall_height = HEIGHT
            else:
                wall_height = min(int(HEIGHT / (distance * cos_angle)), HEIGHT)
            
            start_y = (HEIGHT - wall_height) // 2
            end_y = start_y + wall_height
            
            color_intensity = min(255, max(50, 255 - int(distance * 25)))
            pygame.draw.line(screen, (color_intensity, 0, 0), (x, start_y), (x, end_y))
            
            pygame.draw.line(screen, (50, 50, 50), (x, end_y), (x, HEIGHT))
            pygame.draw.line(screen, (100, 100, 100), (x, 0), (x, start_y))
        else:
            pygame.draw.line(screen, (50, 50, 50), (x, HEIGHT // 2), (x, HEIGHT))
            pygame.draw.line(screen, (100, 100, 100), (x, 0), (x, HEIGHT // 2))

running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                map_data = generate_map()
    
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
    
    screen.fill(BLACK)
    
    draw_3d_scene()
    
    map_scale = 4
    for y in range(MAP_SIZE):
        for x in range(MAP_SIZE):
            if map_data[y][x] == 1:
                pygame.draw.rect(screen, WHITE, (x * map_scale, y * map_scale, map_scale, map_scale))
    
    pygame.draw.circle(screen, RED, (int(player_pos.x * map_scale), int(player_pos.y * map_scale)), 2)
    
    end_x = int(player_pos.x * map_scale + math.cos(player_angle * math.pi / 180) * 5)
    end_y = int(player_pos.y * map_scale + math.sin(player_angle * math.pi / 180) * 5)
    pygame.draw.line(screen, GREEN, (int(player_pos.x * map_scale), int(player_pos.y * map_scale)), (end_x, end_y), 1)
    
    pygame.display.flip()
    
    clock.tick(60)

pygame.quit()