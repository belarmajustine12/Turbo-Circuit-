import pygame
import time
import random

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

pygame.init()
WIDTH, HEIGHT = 600, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TURBO CIRCUIT — Group 6")

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (220, 50, 50)
BLUE = (50, 80, 220)
GREEN = (50, 200, 50)
GRAY = (60, 60, 60)
ROAD_COLOR = (80, 80, 80)
LINE_COLOR = (255, 255, 0)

start_pos = get_start_position()
car_x, car_y = start_pos
car_width, car_height = 50, 80
car_speed = 6

opponents = []
OPP_WIDTH, OPP_HEIGHT = 50, 80
base_opp_speed = 4

score = 0
lap_start_time = time.time()
leaderboard = []
track_sections = ["Start/Finish", "Straightaway", "Sharp Turn", "Tunnel", "Final Straight"]
clock = pygame.time.Clock()
running = True
game_active = True
lap_count = 0
distance_lines = 0
upgrade_items = []

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
        if keys[pygame.K_LEFT] and car_x > 60:
            car_x -= car_speed
        if keys[pygame.K_RIGHT] and car_x < WIDTH - 60 - car_width:
            car_x += car_speed
        if keys[pygame.K_UP] and car_y > 10:
            car_y -= car_speed
        if keys[pygame.K_DOWN] and car_y < HEIGHT - car_height - 10:
            car_y += car_speed
        
        if random.randint(0, 100) < 4:
            spawn_opponent()
        if random.randint(0, 400) < 2:
            spawn_upgrade()
        
        for opp in opponents[:]:
            opp["y"] += opp["speed"]
            if opp["y"] > HEIGHT:
                opponents.remove(opp)
                score += 15
            if check_collision(car_x, car_y, car_width, car_height,
                              opp["x"], opp["y"], OPP_WIDTH, OPP_HEIGHT):
                game_active = False
                lap_time = time.time() - lap_start_time
                new_entry = {"name": f"Racer{lap_count + 1}", "time": lap_time}
                insertion_sort(leaderboard, new_entry)
                update_racer_time(lap_time)
                lap_count += 1
        
        for item in upgrade_items[:]:
            item["y"] += 3
            if item["y"] > HEIGHT:
                upgrade_items.remove(item)
            elif not item["collected"] and check_collision(
                car_x, car_y, car_width, car_height,
                item["x"], item["y"], 30, 30
            ):
                item["collected"] = True
                upgrades[item["type"]] += 1
                add_achievement(f"Got {item['type']} boost!")
                score += 20
        
        elapsed = time.time() - lap_start_time
        score = int(elapsed * 10)
        
        pygame.draw.rect(screen, BLUE, (car_x, car_y, car_width, car_height), border_radius=8)
        pygame.draw.rect(screen, WHITE, (car_x + 10, car_y + 15, 30, 15))
        
        for opp in opponents:
            pygame.draw.rect(screen, RED, (opp["x"], opp["y"], OPP_WIDTH, OPP_HEIGHT), border_radius=8)
        
        for item in upgrade_items:
            if not item["collected"]:
                pygame.draw.circle(screen, GREEN, (item["x"] + 15, item["y"] + 15), 15)
        
        font = pygame.font.Font(None, 36)
        screen.blit(font.render(f"Score: {score}", True, WHITE), (10, 10))
        screen.blit(font.render(f"Laps: {racer['total_laps']}", True, WHITE), (10, 45))
        if racer["best_time"]:
            screen.blit(font.render(f"Best: {racer['best_time']:.2f}s", True, WHITE), (10, 80))
        screen.blit(font.render(f"Points: {racer['championship_points']}", True, WHITE), (WIDTH - 150, 10))
        
        if score >= 50 and "Speedway" not in unlocked_tracks:
            unlock_track("Speedway Circuit")
        if score >= 150 and "Mountain Pass" not in unlocked_tracks:
            unlock_track("Mountain Pass")
    else:
        big_font = pygame.font.Font(None, 72)
        small_font = pygame.font.Font(None, 36)
        
        over = big_font.render("RACE FINISHED!", True, GREEN)
        restart = small_font.render("R = Restart  L = Leaderboard  Q = Quit", True, WHITE)
        final_score = small_font.render(f"Final Score: {score}", True, WHITE)
        
        screen.blit(over, (WIDTH // 2 - 210, HEIGHT // 2 - 100))
        screen.blit(final_score, (WIDTH // 2 - 110, HEIGHT // 2 - 20))
        screen.blit(restart, (WIDTH // 2 - 260, HEIGHT // 2 + 60))
        
        y_pos = HEIGHT // 2 + 130
        screen.blit(small_font.render("TOP TIMES:", True, WHITE), (WIDTH // 2 - 90, y_pos - 30))
        sorted_board = bubble_sort(leaderboard.copy())[:5]
        for i, entry in enumerate(sorted_board):
            text = small_font.render(f"{i + 1}. {entry['name']}: {entry['time']:.2f}s", True, WHITE)
            screen.blit(text, (WIDTH // 2 - 100, y_pos + i * 35))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
print("\nRACE SUMMARY")
print(f"Total Laps: {racer['total_laps']}")
print(f"Best Time: {racer['best_time']:.2f}s" if racer['best_time'] else "Best Time: N/A")
print(f"Championship Points: {racer['championship_points']}")
print(f"Unlocked Tracks: {unlocked_tracks}")
print(f"Achievements: {achievements}")
