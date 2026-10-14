import pygame
import time
import random

# === SORTING FUNCTIONS ===
def bubble_sort(lap_times):
    n = len(lap_times)
    for i in range(n):
        for j in range(0, n - i - 1):
            if lap_times[j]["time"] > lap_times[j + 1]["time"]:
                lap_times[j], lap_times[j + 1] = lap_times[j + 1], lap_times[j]
    return lap_times

def insertion_sort(leaderboard, new_entry):
    leaderboard.append(new_entry)
    for i in range(1, len(leaderboard)):
        current = leaderboard[i]
        j = i - 1
        while j >= 0 and current["time"] < leaderboard[j]["time"]:
            leaderboard[j + 1] = leaderboard[j]
            j -= 1
        leaderboard[j + 1] = current
    return leaderboard

def selection_sort(times_list):
    for i in range(len(times_list)):
        best_index = i
        for j in range(i + 1, len(times_list)):
            if times_list[j]["time"] < times_list[best_index]["time"]:
                best_index = j
        times_list[i], times_list[best_index] = times_list[best_index], times_list[i]
    return times_list

def traverse_circuit(sections, index=0):
    if index >= len(sections):
        return ["✅ Circuit finished!"]
    result = [f"Section {index + 1}: {sections[index]}"]
    result.extend(traverse_circuit(sections, index + 1))
    return result

def get_start_position():
    return (250, 500)

# === GAME DATA ===
unlocked_tracks = set()
achievements = set()

def unlock_track(track_name):
    unlocked_tracks.add(track_name)

def add_achievement(title):
    achievements.add(title)

racer = {
    "name": "Player",
    "total_laps": 0,
    "best_time": None,
    "championship_points": 0
}

upgrades = {"speed": 0, "handling": 0, "acceleration": 0}

def update_racer_time(time_seconds):
    racer["total_laps"] += 1
    if racer["best_time"] is None or time_seconds < racer["best_time"]:
        racer["best_time"] = time_seconds
    racer["championship_points"] += max(100 - int(time_seconds), 10)

# === PYGAME SETUP ===
pygame.init()
WIDTH, HEIGHT = 600, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TURBO CIRCUIT — Group 6")

# COLORS
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (220, 50, 50)
BLUE = (50, 80, 220)
GREEN = (50, 200, 50)
GRAY = (60, 60, 60)
ROAD_COLOR = (80, 80, 80)
LINE_COLOR = (255, 255, 0)

# CAR & GAME SETTINGS
start_pos = get_start_position()
car_x, car_y = start_pos
car_width, car_height = 50, 80
car_speed = 6

opponents = []
OPP_WIDTH, OPP_HEIGHT = 50, 80
base_opp_speed = 4

score = 0
lap_start_time = time.time()
last_score_second = 0
leaderboard = []
track_sections = ["Start/Finish", "Straightaway", "Sharp Turn", "Tunnel", "Final Straight"]
clock = pygame.time.Clock()
running = True
game_active = True
lap_count = 0
distance_lines = 0
upgrade_items = []

# === FUNCTIONS ===
def spawn_opponent():
    lanes = [100, 200, 300, 400, 500]
    lane = random.choice(lanes)
    opponents.append({"x": lane - OPP_WIDTH // 2, "y": -100, "speed": base_opp_speed + random.uniform(0.5, 2)})

def spawn_upgrade():
    types = ["speed", "handling", "acceleration"]
    upgrade_items.append({
        "x": random.choice([150, 250, 350, 450]),
        "y": -50,
        "type": random.choice(types),
        "collected": False
    })

def check_collision(obj1_x, obj1_y, w1, h1, obj2_x, obj2_y, w2, h2):
    return (obj1_x < obj2_x + w2 and
            obj1_x + w1 > obj2_x and
            obj1_y < obj2_y + h2 and
            obj1_y + h1 > obj2_y)

# === DRAWING FUNCTIONS ===
PINK = (255, 180, 200)
PALE_PINK = (255, 220, 230)
HOT_PINK = (255, 100, 150)
DARK_PINK = (200, 60, 100)
UPGRADE_COLOR = (100, 200, 100)
TEXT_COLOR = (60, 60, 60)
OPPONENT_COLOR = (220, 50, 50)

font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 28)
title_font = pygame.font.Font(None, 48)
big_font = pygame.font.Font(None, 60)

def draw_text(text, x, y, color=TEXT_COLOR, font_type=font):
    surface = font_type.render(text, True, color)
    screen.blit(surface, (x, y))

def draw_car(x, y, color, w, h, is_player=False):
    pygame.draw.rect(screen, color, (x, y, w, h), border_radius=8)
    if is_player:
        pygame.draw.rect(screen, WHITE, (x + 10, y + 15, w - 20, 20))
        pygame.draw.rect(screen, WHITE, (x + 10, y + 45, w - 20, 20))

# === MAIN GAME LOOP ===
while running:
    screen.fill(GRAY)
    pygame.draw.rect(screen, ROAD_COLOR, (50, 0, WIDTH - 100, HEIGHT))
    
    distance_lines += car_speed
    for i in range(-100, HEIGHT, 80):
        line_y = (i + distance_lines) % HEIGHT
        pygame.draw.rect(screen, LINE_COLOR, (WIDTH // 2 - 3, line_y, 6, 40))
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and not game_active:
            if event.key == pygame.K_r:
                game_active = True
                score = 0
                lap_start_time = time.time()
                last_score_second = 0
                opponents.clear()
                upgrade_items.clear()
                car_x, car_y = start_pos
                lap_count = 0
            if event.key == pygame.K_l:
                print("\nLEADERBOARD — Bubble Sort:")
                for r in bubble_sort(leaderboard.copy()):
                    print(f"  {r['name']}: {r['time']:.2f}s")
                print("\nBest Lap — Selection Sort:")
                best = selection_sort(leaderboard.copy())
                if best:
                    print(f"  Best: {best[0]['name']} — {best[0]['time']:.2f}s")
                print("\nCircuit Path:")
                for step in traverse_circuit(track_sections):
                    print(step)
            if event.key == pygame.K_q:
                running = False
    
    if game_active:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and car_x > 86:
            car_x -= car_speed
        if keys[pygame.K_RIGHT] and car_x < WIDTH - 86 - car_width:
            car_x += car_speed
        if keys[pygame.K_UP] and car_y > 108:
            car_y -= car_speed
        if keys[pygame.K_DOWN] and car_y < HEIGHT - car_height - 8:
            car_y += car_speed

        elapsed = time.time() - lap_start_time
        whole_seconds = int(elapsed)
        if whole_seconds > last_score_second:
            score += whole_seconds - last_score_second
            last_score_second = whole_seconds

        if random.randint(0, 100) < 4:
            spawn_opponent()
        if random.randint(0, 400) < 2:
            spawn_upgrade()

        for opp in opponents[:]:
            opp["y"] += opp["speed"]
            if opp["y"] > HEIGHT:
                opponents.remove(opp)
                score += 15
                add_achievement("Opponent Dodger")
            elif check_collision(car_x, car_y, car_width, car_height,
                                 opp["x"], opp["y"], OPP_WIDTH, OPP_HEIGHT):
                game_active = False
                lap_time = time.time() - lap_start_time
                new_entry = {
                    "name": f"Player Run {lap_count + 1}",
                    "time": lap_time,
                    "score": score
                }
                insertion_sort(leaderboard, new_entry)
                update_racer_time(lap_time)
                lap_count += 1
                break

        for item in upgrade_items[:]:
            item["y"] += 3
            if item["y"] > HEIGHT:
                upgrade_items.remove(item)
            elif check_collision(car_x, car_y, car_width, car_height,
                                 item["x"], item["y"], 30, 30):
                upgrades[item["type"]] += 1
                add_achievement(f"Got {item['type']} boost!")
                score += 20
                upgrade_items.remove(item)

        if score >= 50:
            unlock_track("Speedway Circuit")
        if score >= 150:
            unlock_track("Mountain Pass")

        draw_car(car_x, car_y, PINK, car_width, car_height, True)
        for opp in opponents:
            draw_car(opp["x"], opp["y"], OPPONENT_COLOR, OPP_WIDTH, OPP_HEIGHT)
        for item in upgrade_items:
            pygame.draw.circle(screen, UPGRADE_COLOR,
                               (int(item["x"] + 15), int(item["y"] + 15)), 15)
            draw_text("+", item["x"] + 8, item["y"] + 3, DARK_PINK, font)

        pygame.draw.rect(screen, PALE_PINK, (10, 108, 190, 105), border_radius=12)
        pygame.draw.rect(screen, PALE_PINK, (WIDTH - 205, 108, 195, 105), border_radius=12)
        draw_text(f"SCORE: {score}", 23, 119, HOT_PINK)
        draw_text(f"Runs: {racer['total_laps']}", 23, 153)
        best_label = f"Best: {racer['best_time']:.1f}s" if racer["best_time"] is not None else "Best: --"
        draw_text(best_label, 23, 184, TEXT_COLOR, small_font)

        draw_text("CHAMPIONSHIP", WIDTH - 192, 119, DARK_PINK, small_font)
        draw_text(f"{racer['championship_points']} points", WIDTH - 192, 149, HOT_PINK)
        draw_text(f"Upgrades: {sum(upgrades.values())}", WIDTH - 192, 181, DARK_PINK, small_font)

        draw_text("TURBO CIRCUIT", 165, 17, DARK_PINK, title_font)
        draw_text("♡ PINK EDITION ♡", 215, 62, DARK_PINK, small_font)
        draw_text("Survive +1/sec  |  Dodge +15  |  Upgrade +20",
                  88, HEIGHT - 27, WHITE, small_font)

    else:
        pygame.draw.rect(screen, PALE_PINK, (30, 130, WIDTH - 60, HEIGHT - 160),
                         border_radius=24)
        pygame.draw.rect(screen, HOT_PINK, (30, 130, WIDTH - 60, HEIGHT - 160),
                         width=4, border_radius=24)

        draw_text("RACE FINISHED!", 95, 157, HOT_PINK, big_font)
        draw_text(f"Final Score: {score}", 160, 225, DARK_PINK, title_font)
        draw_text(f"Championship Points: {racer['championship_points']}",
                  95, 278, DARK_PINK, font)
        draw_text(f"Total Runs: {racer['total_laps']}", 190, 315)
        if racer["best_time"] is not None:
            draw_text(f"Best Time: {racer['best_time']:.2f}s", 180, 350)

        draw_text("TOP LAP TIMES", 205, 395, HOT_PINK, font)
        sorted_board = bubble_sort(leaderboard)[:5]
        for i, entry in enumerate(sorted_board):
            draw_text(f"{i + 1}. {entry['name']}: {entry['time']:.2f}s",
                      145, 430 + i * 27, DARK_PINK, small_font)

        draw_text("R = Restart", 72, 605, HOT_PINK, small_font)
        draw_text("L = Leaderboard", 225, 605, HOT_PINK, small_font)
        draw_text("Q = Quit", 420, 605, HOT_PINK, small_font)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
