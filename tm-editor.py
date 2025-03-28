import pygame
import json

# Initialisation de pygame
pygame.init()

# Constantes
tile_size = 32
grid_width = 20
grid_height = 15
screen_width = grid_width * tile_size * 2 + 200  # Ajout d'espace pour l'UI
screen_height = grid_height * tile_size
max_height = 3  # Hauteur max pour les tiles
height_offset = 10  # Décalage en hauteur
ui_width = 200  # Largeur de la zone UI

# Couleurs
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)

# Chargement des tiles (placeholders avec des couleurs différentes)
tiles = [pygame.Surface((tile_size, tile_size)) for _ in range(8)]
colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0),
          (255, 165, 0), (128, 0, 128), (0, 255, 255), (192, 192, 192)]
tile_names = ["C_in", "C_out_C", "C_out_L", "C_out_R", "Side", "terrain_1", "terrain_2", "terrain_3"]
for i, color in enumerate(colors):
    tiles[i].fill(color)

# Grille vide (niveau, hauteur et rotation)
level = [[-1 for _ in range(grid_width)] for _ in range(grid_height)]
height_map = [[0 for _ in range(grid_width)] for _ in range(grid_height)]
rotation_map = [[0 for _ in range(grid_width)] for _ in range(grid_height)]  # Rotation en degrés (0, 90, 180, 270)

current_tile = 0
current_height = 0
current_rotation = 0  # Rotation actuelle en degrés (0, 90, 180, 270)

# Fenêtre
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Tilemap Editor - Isométrique, Cartésien et UI")

iso_grid_height = grid_height * tile_size // 4
center_offset_y = (screen_height - iso_grid_height) // 2

def cart_to_iso(x, y, h):
    iso_x = (x - y) * tile_size // 2 + screen_width // 5 * 3
    iso_y = (x + y) * tile_size // 4 - h * (tile_size // 2) + center_offset_y
    return iso_x, iso_y

def create_shadow(tile_size):
    # Créer une surface avec dégradé (noir vers transparent)
    shadow_surface = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
    for y in range(tile_size):
        intensity = int(255 * (1 - y / tile_size))  # Dégradé du noir au transparent
        pygame.draw.line(shadow_surface, (0, 0, 0, intensity), (0, y), (tile_size, y))
    return shadow_surface

def draw_tile_with_shadow(tile, x, y, rotation=0):
    # Créer une ombre avec dégradé
    shadow_surface = create_shadow(tile_size)

    # Définir un léger décalage pour l'ombre
    shadow_offset = 5  # Décalage de l'ombre
    screen.blit(shadow_surface, (x + shadow_offset, y + shadow_offset))  # Ombre

    # Appliquer la rotation à la tuile
    rotated_tile = pygame.transform.rotate(tile, rotation)
    rotated_rect = rotated_tile.get_rect(center=(x + tile_size // 2, y + tile_size // 2))
    screen.blit(rotated_tile, rotated_rect.topleft)

def draw_rotation_indicator(x, y, rotation):
    match rotation:
        case 0:  # Ligne en bas
            start_pos = (x, y + tile_size - 2)
            end_pos = (x + tile_size, y + tile_size - 2)
        case 90:  # Ligne à droite
            start_pos = (x + tile_size - 2, y)
            end_pos = (x + tile_size - 2, y + tile_size)
        case 180:  # Ligne en haut
            start_pos = (x, y + 2)
            end_pos = (x + tile_size, y + 2)
        case 270:  # Ligne à gauche
            start_pos = (x + 2, y)
            end_pos = (x + 2, y + tile_size)
        case _:  # Cas par défaut (rotation invalide)
            return  # Ne rien dessiner si la rotation est invalide

    # Dessiner la ligne noire
    pygame.draw.line(screen, BLACK, start_pos, end_pos, 2)

def draw_ui():
    pygame.draw.rect(screen, WHITE, (screen_width - ui_width, 0, ui_width, screen_height))
    font = pygame.font.Font(None, 24)

    # Affichage des boutons de sélection de tile
    for i, (tile, name) in enumerate(zip(tiles, tile_names)):
        y_pos = 20 + i * (tile_size + 5)
        screen.blit(tile, (screen_width - ui_width + 10, y_pos))
        text = font.render(name, True, BLACK)
        screen.blit(text, (screen_width - ui_width + 50, y_pos + 5))

    # Affichage des boutons de hauteur
    height_buttons_start_y = screen_height - 150  # Remonter les boutons de hauteur
    for i in range(max_height + 1):
        y_pos = height_buttons_start_y + i * 20
        color = BLUE if i == current_height else GRAY
        pygame.draw.rect(screen, color, (screen_width - ui_width + 10, y_pos, 50, 20))
        text = font.render(str(i), True, BLACK)
        screen.blit(text, (screen_width - ui_width + 30, y_pos + 5))

    # Bouton de rotation
    rotation_button_y = screen_height - 125
    pygame.draw.rect(screen, GRAY, (screen_width - ui_width + 65, rotation_button_y, 130, 30))
    rotation_text = font.render(f"Rotation: {current_rotation}°", True, BLACK)
    screen.blit(rotation_text, (screen_width - ui_width + 75, rotation_button_y + 5))

    # Bouton de sauvegarde
    save_button_y = screen_height - 50
    pygame.draw.rect(screen, GRAY, (screen_width - ui_width + 10, save_button_y, 180, 30))
    save_text = font.render("Sauvegarder", True, BLACK)
    screen.blit(save_text, (screen_width - ui_width + 50, save_button_y + 5))

def export_map_to_json(file_path):
    # Dimensions de la carte
    map_data = {
        "width": grid_width,
        "height": grid_height,
        "tiles": []
    }

    # Parcourir la grille et encoder les données
    for y in range(grid_height):
        for x in range(grid_width):
            tile_type = level[y][x]
            tile_height = height_map[y][x]
            tile_rotation = rotation_map[y][x] // 90  # Convertir la rotation en index (0, 1, 2, 3)

            if tile_type == -1:  # Si aucune tuile n'est placée
                packed_value = 0  # Valeur par défaut
            else:
                packed_value = (tile_height << 5) | (tile_rotation << 3) | (tile_type & 0b111)  # Encoder hauteur, rotation et type

            map_data["tiles"].append(packed_value)

    # Écrire les données dans un fichier JSON
    with open(file_path, "w") as json_file:
        json.dump(map_data, json_file, indent=4)
    print(f"Carte exportée avec succès dans {file_path}")

def import_map_from_json(file_path):
    try:
        with open(file_path, "r") as json_file:
            map_data = json.load(json_file)

        # Vérifier les dimensions
        if map_data["width"] != grid_width or map_data["height"] != grid_height:
            print("Les dimensions de la carte importée ne correspondent pas à la grille actuelle.")
            return

        # Initialiser les grilles avec les données importées
        for y in range(grid_height):
            for x in range(grid_width):
                packed_value = map_data["tiles"][y * grid_width + x]
                tile_type = packed_value & 0b111  # Extraire les 3 bits de poids faible
                tile_height = packed_value >> 3  # Décalage pour extraire la hauteur
                level[y][x] = tile_type
                height_map[y][x] = tile_height

        print(f"Carte importée avec succès depuis {file_path}")
    except FileNotFoundError:
        print(f"Fichier {file_path} introuvable. Une nouvelle carte sera créée.")
    except Exception as e:
        print(f"Erreur lors de l'importation de la carte : {e}")

# Importer la carte si le fichier existe
import_map_from_json("exported_map.json")

running = True
while running:
    screen.fill(WHITE)

    # Affichage de la grille cartésienne (édition)
    for y in range(grid_height):
        for x in range(grid_width):
            tile_index = level[y][x]
            pygame.draw.rect(screen, GRAY, (x * tile_size, y * tile_size, tile_size, tile_size), 1)
            if tile_index != -1:
                draw_tile_with_shadow(tiles[tile_index], x * tile_size, y * tile_size, rotation_map[y][x])
                draw_rotation_indicator(x * tile_size, y * tile_size, rotation_map[y][x])

    # Affichage de la grille avec projection isométrique
    for y in range(grid_height):
        for x in range(grid_width):
            tile_index = level[y][x]
            tile_height = height_map[y][x]
            iso_x, iso_y = cart_to_iso(x, y, tile_height)
            if tile_index != -1:
                draw_tile_with_shadow(tiles[tile_index], iso_x, iso_y)
            pygame.draw.rect(screen, GRAY, (iso_x, iso_y, tile_size // 2, tile_size // 4), 1)

    # Affichage de l'UI
    draw_ui()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos

            if mouse_x < screen_width - ui_width:  # Clic sur la grille cartésienne
                grid_x = mouse_x // tile_size
                grid_y = mouse_y // tile_size
                if 0 <= grid_x < grid_width and 0 <= grid_y < grid_height:
                    if event.button == 1:  # Clic gauche -> Placer un tile
                        level[grid_y][grid_x] = current_tile
                        height_map[grid_y][grid_x] = current_height
                        rotation_map[grid_y][grid_x] = current_rotation  # Appliquer la rotation actuelle
                    elif event.button == 3:  # Clic droit -> Tourner la tuile
                        if level[grid_y][grid_x] != -1:  # Si une tuile est placée
                            rotation_map[grid_y][grid_x] = (rotation_map[grid_y][grid_x] + 90) % 360
                            print(f"Rotation de la tuile à ({grid_x}, {grid_y}): {rotation_map[grid_y][grid_x]}°")

            else:  # Clic sur l'UI
                for i in range(len(tiles)):
                    y_pos = 20 + i * (tile_size + 5)
                    if screen_width - ui_width + 10 <= mouse_x <= screen_width - ui_width + 50 and y_pos <= mouse_y <= y_pos + tile_size:
                        current_tile = i
                        print(f"Tile sélectionné: {tile_names[current_tile]}")

                # Ajuster la position de départ des boutons de hauteur
                height_buttons_start_y = screen_height - 150  # Correspond à la nouvelle position
                for i in range(max_height + 1):
                    y_pos = height_buttons_start_y + i * 20
                    if screen_width - ui_width + 10 <= mouse_x <= screen_width - ui_width + 60 and y_pos <= mouse_y <= y_pos + 20:
                        current_height = i
                        print(f"Hauteur sélectionnée: {current_height}")

                # Vérifier si le bouton de rotation est cliqué
                rotation_button_y = screen_height - 100
                if screen_width - ui_width + 10 <= mouse_x <= screen_width - ui_width + 190 and rotation_button_y <= mouse_y <= rotation_button_y + 30:
                    current_rotation = (current_rotation + 90) % 360
                    print(f"Rotation actuelle: {current_rotation}°")

                # Vérifier si le bouton de sauvegarde est cliqué
                save_button_y = screen_height - 50
                if screen_width - ui_width + 10 <= mouse_x <= screen_width - ui_width + 190 and save_button_y <= mouse_y <= save_button_y + 30:
                    export_map_to_json("exported_map.json")
                    print("Carte sauvegardée dans 'exported_map.json'")

    pygame.display.flip()

pygame.quit()
