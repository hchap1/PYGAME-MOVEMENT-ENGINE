#GRAPHICAL LEVEL EDITOR PROGRAM

#RUN THE PROGRAM (DUH)
#IF YOU WANT TO EDIT AN EXISTING LEVEL, ENTER E INTO THE TERMINAL.
#   THEN, ENTER THE LEVEL NUMBER (e.g. 10)

#IF YOU WANT TO CREATE A NEW LEVEL, ENTER C INTO THE TERMINAL.
#   ENTER THE LEVEL NUMBER. YOU CAN CHOOSE AN EXISTING LEVEL NUMBER AND IT WILL NOT REPLACE THE LEVEL, BUT RATHER
#       SHIFT ALL LATER LEVELS ONE OVER TO MAKE ROOM FOR YOUR NEW LEVEL. THIS IS HELPFUL IF YOU WANT TO CREATE
#       AN EASIER LEVEL CLOSE TO THE START WITHOUT DELETING THE HARDER (AND MORE FRUSTRATING) LEVELS.
#   ENTER THE WIDTH AND HEIGHT IN LEVELS (I RECOMMEND 20x20)
#   ENTER THE RGB OF THE BACKGROUND. 135, 206, 235 IS THE SKY BLUE USED IN DIRT THEMED LEVELS, 10, 20, 50 IS THE DARK BLUE IN LATER LEVELS.
#   FOLLOW THE MAIN INSTRUCTION SET BELOW.

#MAIN INSTRUCTIONS FOR EDITOR
#   THE GRAPHIC LEVEL EDITOR WILL OPEN (HOPEFULLY)
#   MOVE AROUND WITH WASD, PRESS NUMBER KEYS TO REPLACE BLOCKs
#   PRESS 'O' (the letter) TO SET THE LOCATION FOR SPAWN POINT ONE (before they beat the level)
#   PRESS 'P' TO SET THE LOCATION FOR SPAWN POINT TWO (for after they beat the level when they come back through)
#   BLOCKS ARE:
#       1-DIRT, 2-UPWARDS SPIKE, 3-SPIKE POINTING TO THE RIGHT, 4-SPIKE FACING DOWN, 5-SPIKE POINTING TO THE LEFT
#       6-TELEPORT TO PREVIOUS LEVEL ON CONTACT, 7-TELEPORT TO THE NEXT LEVEL ON CONTACT
#       8-BLUE-GRAY STONE BRICKS (lower friction than dirt), 9-NO-CLIP DASH PAD
#   WHEN YOU ARE DONE, HIT ENTER. THE GRAPHICAL LEVEL EDITOR WILL CLOSE. DO NOT STOP THE PROGRAM - YOU NEED TO PUT 'S' INTO THE TERMINAL TO SAVE.
#   MAKE SURE TO RECORD A SKIP REPLAY FOR YOUR LEVEL!



import pygame, os

#REPLACE WITH FILEPATH TO YOUR GAME FOLDER REPLACE BACKSLASHES WITH DOUBLE BACKSLASHES: \ -> \\ LEAVE A DOUBLE BACKSLASH AT THE END.
GLOBAL_PATH = "C:\\users\\hchap\\Onedrive\\.PYGAME MOVEMENT ENGINE\\"


global_scale = 80
numbers = "0123456789"
tile_names = {}
    
with open(GLOBAL_PATH + "gamefiles\\tilemapIDs.txt") as textfile:
    for line in textfile.readlines():
        index, name = (line.strip("\n")).split(" ")
    tile_names[index] = name.upper()

target_level = input("[E]dit level or [C]reate level?").lower()[0]

def render(tilemap, camera_position):
    x, y = camera_position
    for row in range(len(tilemap)):
        for tile in range(len(tilemap[row])):
            index = int(tilemap[row][tile])
            if tile_data_by_ID[index + 1][4] == "1":
                try: screen.blit(tile_assets[index], [tile * global_scale + x, row * global_scale + y])
                except: pass
    count = 0
    for asset in tile_assets: 
        count += 1
        if asset == 0:
            text = font.render(, True, (255,255,255), (0,0,0))
            screen.blit(text, (10, 10))
        else:
            screen.blit(asset)   

current_tilemap = []
current_spawn = [0, 0]
current_spawn_2 = [0, 0]

if target_level == "e":
    level_path = GLOBAL_PATH + "gamefiles\\roomdata\\%s\\" % input("LEVEL ID %s" % os.listdir("gamefiles\\roomdata\\"))
    pygame.init()
    screen = pygame.display.set_mode([1920,1080])
    screen.fill((255,255,255))
    clock = pygame.time.Clock()
    font = pygame.font.Font('freesansbold.ttf', 25)
    with open(GLOBAL_PATH + "gamefiles\\tiledatabyID.txt", "r") as data:
        tile_data_by_ID = [x.strip("\n").split(" ") for x in data.readlines()]

    with open(GLOBAL_PATH + "gamefiles\\tiledatabyID.txt", "r") as tiledata:
        data_by_id = [x.strip("\n") for x in tiledata.readlines()]
        tile_assets = [0]
        for asset in os.listdir("assets\\tiles"):
            if ".png" in asset and asset[0] in numbers:
                image = 0
                if data_by_id[int(asset.split(".")[0]) + 1].split(" ")[4] == "1":
                    image = pygame.transform.scale(pygame.image.load("assets\\tiles\\%s" % asset).convert_alpha(), [global_scale, global_scale])
                tile_assets.append(image)

    tile_assets[6] = pygame.transform.scale(pygame.image.load("assets\\tiles\\entry.png").convert_alpha(), [global_scale, global_scale])
    tile_assets[7] = pygame.transform.scale(pygame.image.load("assets\\tiles\\exit.png").convert_alpha(), [global_scale, global_scale])
    spawn_one_asset = pygame.transform.scale(pygame.image.load("assets\\tiles\\spawn.png").convert_alpha(), [global_scale, global_scale])
    spawn_two_asset = pygame.transform.scale(pygame.image.load("assets\\tiles\\spawn2.png").convert_alpha(), [global_scale, global_scale])
    current_tilemap = []
    with open("%stilemap.txt" % level_path, "r") as data:
        lines = data.readlines()
        for line in lines:
            temp = []
            [temp.append(x) if x != "\n" else 0 for x in line]
            current_tilemap.append(temp)

    with open("%s\\roominfo.txt" % level_path, "r") as data:
        name, current_spawn, current_spawn_2, current_bg = [x.strip("\n") for x in data.readlines()]
        current_spawn = [int(x) for x in current_spawn.split(", ")]
        current_spawn_2 = [int(x) for x in current_spawn_2.split(", ")]
        current_bg = [int(x) for x in current_bg.split(", ")]

    x = 0
    y = 0

    running = True
    while running:
        screen.fill(current_bg)
        dt = clock.tick(60)
        keys = pygame.key.get_pressed()
        horizontal_axis = 0
        vertical_axis = 0
        symbol = "NONE"
        changing_spawn_one = False
        changing_spawn_two = False
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    vertical_axis += global_scale
                if event.key == pygame.K_a:
                    horizontal_axis += global_scale
                if event.key == pygame.K_s:
                    vertical_axis -= global_scale
                if event.key == pygame.K_d:
                    horizontal_axis -= global_scale
                if event.key >= 48 and event.key <= 58:
                    symbol = str(event.key - 48)
                if event.key == pygame.K_o:
                    changing_spawn_one = True
                if event.key == pygame.K_p:
                    changing_spawn_two = True
                if event.key == pygame.K_RETURN:
                    running = False
            if event.type == pygame.QUIT:
                running = False
        x += horizontal_axis
        y += vertical_axis
        render(current_tilemap, [x + 960, y + 540])
        block_x = -int(x / global_scale)
        block_y = -int(y / global_scale)
        if symbol != "NONE": current_tilemap[block_y][block_x] = symbol 
        if changing_spawn_one:
            if block_x != current_spawn[0] or block_y != current_spawn[1]:
                current_spawn = [block_x, block_y]

        if changing_spawn_two:
            if block_x != current_spawn_2[0] or block_y != current_spawn_2[1]:
                current_spawn_2 = [block_x, block_y]

        screen.blit(spawn_one_asset, [current_spawn[0] * global_scale + 960 + x, current_spawn[1] * global_scale + 540 + y])
        screen.blit(spawn_two_asset, [current_spawn_2[0] * global_scale + 960 + x, current_spawn_2[1] * global_scale + 540 + y])
                        
        pygame.draw.rect(screen, (219, 172, 52), pygame.Rect(960, 540, global_scale, global_scale), width=5)
        pygame.display.update()

    pygame.quit()

    action = input("[S]ave or [D]iscard?\n> ")[0].lower()
    if action == "s":
        new_tilemap = ""
        for row in current_tilemap:
            new_tilemap += "".join(row) + "\n"
        with open(level_path + "\\tilemap.txt", "w") as tilemap:
            tilemap.write(new_tilemap)
        with open(level_path + "\\roominfo.txt", "w") as roominfo:
            roominfo.write("%s\n%s\n%s\n%s" % (name, ", ".join([str(x) for x in current_spawn]), ", ".join([str(x) for x in current_spawn_2]), ", ".join([str(x) for x in current_bg])))

if target_level == "c":
    level_path = input("LEVEL ID:\n> ")
    existing_directories = os.listdir(GLOBAL_PATH + "gamefiles\\roomdata\\")
    bad = ["1", "11", "12", "20", "2", "3", "4"]

    single_digit = []
    double_digit = []
    triple_digit = []
    quadruple_digit = []

    for item in existing_directories:
        if len(item) == 1:
            single_digit.append(item)
        elif len(item) == 2:
            double_digit.append(item)
        elif len(item) == 3:
            triple_digit.append(item)
        elif len(item) == 4:
            quadruple_digit.append(item)

    existing_directories = single_digit + double_digit + triple_digit + quadruple_digit
    last_level = existing_directories[len(existing_directories) - 1]
    if level_path in existing_directories:
        start_shift = level_path
        count = len(existing_directories) + 1
        for directory in range(len(existing_directories) - existing_directories.index(level_path)):
            count -= 1
            os.rename(GLOBAL_PATH + "gamefiles\\roomdata\\%s" % count, GLOBAL_PATH + "gamefiles\\roomdata\\%s" % (int(count) + 1))

    os.mkdir(GLOBAL_PATH + "gamefiles\\roomdata\\%s" % level_path)
    width = int(input("WIDTH IN TILES?\n> "))
    height = int(input("HEIGHT IN TILES?\n> "))
    background_rgb = input("RGB OF BG (E.G. 255, 255, 255)\n> ")
    theme = input("[D]irt, [B]luestone?\n> ")[0].lower()
    level_path = GLOBAL_PATH + "gamefiles\\roomdata\\" + level_path
    with open(level_path + "\\tilemap.txt", "w") as tilemap:
        if theme == "b": blank_tilemap = "8" * width + "\n"
        else: blank_tilemap = "1" * width + "\n"
        for row in range(height - 2):
            temp = ""
            for tile in range(width):
                temp += "0"
            if theme == "b":
                temp = "8" + temp[1:len(temp) - 1] + "8"
            else:
                temp = "1" + temp[1:len(temp) - 1] + "1"
            blank_tilemap += temp + "\n"
        if theme == "b": tilemap.write(blank_tilemap + "8" * width)
        else: tilemap.write(blank_tilemap + "1" * width)
        
    
    pygame.init()
    screen = pygame.display.set_mode([1920,1080])
    screen.fill((255,255,255))
    clock = pygame.time.Clock()
    font = pygame.font.Font('freesansbold.ttf', 25)

    with open(GLOBAL_PATH + "gamefiles\\tiledatabyID.txt", "r") as tiledata:
        tile_data_by_ID = [x.strip("\n") for x in tiledata.readlines()]
        tile_assets = [0]
        for asset in os.listdir("assets\\tiles"):
            if ".png" in asset and asset[0] in numbers:
                image = 0
                if tile_data_by_ID[int(asset.split(".")[0]) + 1].split(" ")[4] == "1":
                    image = pygame.transform.scale(pygame.image.load("assets\\tiles\\%s" % asset).convert_alpha(), [global_scale, global_scale])
                tile_assets.append(image)
    tile_assets[6] = pygame.transform.scale(pygame.image.load("assets\\tiles\\entry.png").convert_alpha(), [global_scale, global_scale])
    tile_assets[7] = pygame.transform.scale(pygame.image.load("assets\\tiles\\exit.png").convert_alpha(), [global_scale, global_scale])
    spawn_one_asset = pygame.transform.scale(pygame.image.load("assets\\tiles\\spawn.png").convert_alpha(), [global_scale, global_scale])
    spawn_two_asset = pygame.transform.scale(pygame.image.load("assets\\tiles\\spawn2.png").convert_alpha(), [global_scale, global_scale])
    current_tilemap = []
    with open(GLOBAL_PATH + "gamefiles\\roomdata\\%s\\tilemap.txt" % level_path.split("\\")[-1], "r") as data:
        lines = data.readlines()
        for line in lines:
            temp = []
            [temp.append(x) if x != "\n" else 0 for x in line]
            current_tilemap.append(temp)
    name, current_spawn, current_spawn_2, current_bg = ["level%s" % level_path[len(level_path) - 1], [0,0], [0,0], background_rgb]
    current_bg = [int(x) for x in current_bg.split(", ")]
    tile_data_by_ID = [x.split(" ") for x in tile_data_by_ID]

    x = 0
    y = 0

    running = True
    while running:
        screen.fill(current_bg)
        dt = clock.tick(60)
        keys = pygame.key.get_pressed()
        horizontal_axis = 0
        vertical_axis = 0
        symbol = "NONE"
        changing_spawn_one = False
        changing_spawn_two = False
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    vertical_axis += global_scale
                if event.key == pygame.K_a:
                    horizontal_axis += global_scale
                if event.key == pygame.K_s:
                    vertical_axis -= global_scale
                if event.key == pygame.K_d:
                    horizontal_axis -= global_scale
                if event.key >= 48 and event.key <= 58:
                    symbol = str(event.key - 48)
                if event.key == pygame.K_o:
                    changing_spawn_one = True
                if event.key == pygame.K_p:
                    changing_spawn_two = True
                if event.key == pygame.K_RETURN:
                    running = False
            if event.type == pygame.QUIT:
                running = False
        x += horizontal_axis
        y += vertical_axis
        render(current_tilemap, [x + 960, y + 540])
        block_x = -int(x / global_scale)
        block_y = -int(y / global_scale)
        if symbol != "NONE": current_tilemap[block_y][block_x] = symbol 
        if changing_spawn_one:
            if block_x != current_spawn[0] or block_y != current_spawn[1]:
                current_spawn = [block_x, block_y]

        if changing_spawn_two:
            if block_x != current_spawn_2[0] or block_y != current_spawn_2[1]:
                current_spawn_2 = [block_x, block_y]

        screen.blit(spawn_one_asset, [current_spawn[0] * global_scale + 960 + x, current_spawn[1] * global_scale + 540 + y])
        screen.blit(spawn_two_asset, [current_spawn_2[0] * global_scale + 960 + x, current_spawn_2[1] * global_scale + 540 + y])
                        
        pygame.draw.rect(screen, (219, 172, 52), pygame.Rect(960, 540, global_scale, global_scale), width=5)
        pygame.display.update()

    pygame.quit()

    action = input("[S]ave or [D]iscard?\n> ")[0].lower()
    if action == "s":
        new_tilemap = ""
        for row in current_tilemap:
            new_tilemap += "".join(row) + "\n"
        with open(level_path + "\\tilemap.txt", "w") as tilemap:
            tilemap.write(new_tilemap)
        with open(level_path + "\\roominfo.txt", "w") as roominfo:
            roominfo.write("%s\n%s\n%s\n%s" % (name, ", ".join([str(x) for x in current_spawn]), ", ".join([str(x) for x in current_spawn_2]), ", ".join([str(x) for x in current_bg])))