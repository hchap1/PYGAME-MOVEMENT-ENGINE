#WELCOME TO MY PYGAME / PYTHON PHYSICS ENGINE. 
#THERE ARE A FAIR FEW LEVELS MADE TO TEST ALL THE FEATURES!

#BEFORE YOU CAN PLAY, MAKE SURE TO READ THE CONTROLS BELOW

"AND MOST IMPORTANTLY, REPLACE THE BELOW STRING WITH THE ABSOLUTE FILE PATH TO THE .PYGAME MOVEMENT ENGINE FOLDER, INCLUDING .PYGAME MOVEMENT ENGINE"
"MAKE SURE TO USE DOUBLE BLACKSLASH!"
"AFTER YOU HAVE UNZIPPED, YOU CAN NAVIGATE TO THE .PYGAME MOVEMENT ENGINE FOLDER, RIGHT CLICK, AND PRESS COPY AS PATH."
"PASTE THAT IN BELOW AND REPLACE ALL BACKSLASHES WITH DOUBLE BACKSLASHES"

GLOBAL_PATH = "C:\\users\\hchap\\Onedrive\\.PYGAME MOVEMENT ENGINE\\" #EXAMPLE ONLY - REPLACE WITH REAL FILEPATH

#CONTROLS
# A & D for left and right
# SPACE is jump
# LSHIFT is crouch
# APOSTROPHE is dash
# F is skip level (TRY THIS IT'S SUPER COOL)

#ADVANCED
# Press R to start recording a replay for your own level skips (start at the start, press R. YOU CANNOT GO ACROSS LEVELS - THIS CLEARS THE RECORDING CACHE. 
# Make sure to press R before going to the next level to save the recording.)

# See level_editor.py if you want to make your own levels, or edit existing levels.


















import pygame, os, math, time

pygame.init()
screen = pygame.display.set_mode([1920,1080])
screen.fill((255,255,255))
clock = pygame.time.Clock()
font = pygame.font.Font('freesansbold.ttf', 25)

half_screen_x, half_screen_y = [x / 2 for x in screen.get_size()]
tilescale = 5
numbers = "0123456789"

particle_assets = {}
for asset in os.listdir("assets\\particles"):
    if ".png" in asset:
        particle_assets[asset.strip(".png")] = pygame.image.load("assets\\particles\\%s" % asset).convert_alpha()

def load_tiles():
    with open(GLOBAL_PATH + "gamefiles\\tiledatabyID.txt", "r") as tiledata:
        data_by_id = [x.strip("\n") for x in tiledata.readlines()]
    tile_assets = [0]
    for asset in os.listdir("assets\\tiles"):
        if ".png" in asset and asset[0] in numbers:
            image = 0
            if data_by_id[int(asset.split(".")[0]) + 1].split(" ")[4] == "1":
                image = pygame.image.load("assets\\tiles\\%s" % asset).convert_alpha()
            tile_assets.append(image)
    return tile_assets

def scale_all_tiles(bs, tile_assets):
    temp = []
    for i in range(len(tile_assets)):
        if tile_assets[i] != 0:
            temp.append(pygame.transform.scale(tile_assets[i], (16 * bs, 16 * bs)))
        else:
            temp.append(0)
    return temp

def calculate_player_position_at_tile(tile_position):
    tile_x, tile_y = tile_position
    player_x = tile_x * 16 * tilescale
    player_y = tile_y * -16 * tilescale
    return [player_x, player_y]

def calculate_tile_index_at_position(player_position):
    player_x, player_y = player_position
    tile_x = player_x / (16 * tilescale)
    tile_y = player_y / (-16 * tilescale)
    return [int(tile_y), int(tile_x)]

def calculate_floor_tile_index_at_position(player_position):
    player_x, player_y = player_position
    tile_x = player_x / (16 * tilescale)
    tile_y = player_y / (-16 * tilescale)
    return [math.floor(tile_y), math.floor(tile_x)]

def round_player_position(player_position):
    player_x, player_y = player_position
    tile_x = player_x / (16 * tilescale)
    tile_y = player_y / (-16 * tilescale)
    expected_position = calculate_player_position_at_tile([math.floor(tile_x), math.floor(tile_y)])
    return expected_position

def add_vectors(vector2, change):
    return [vector2[0] + change[0], vector2[1] + change[1]]

def subtract_vectors(vector2, change):
    return [vector2[0] - change[0], vector2[1] - change[1]]

class particle:
    def __init__(self, name, duration, position, isGravity=False, velocity=[0,0], direction=1):
        self.name = name
        self.time_created = time.time()
        self.time_destroyed = time.time() + duration
        self.position = position
        self.gravity = isGravity
        self.velocity = velocity
        self.direction = direction

    def physics(self, player_position):
        self.velocity[1] -= int(self.gravity)
        self.position = add_vectors(self.position, self.velocity)
        my_asset = particle_assets[self.name]
        x, y = [x  * tilescale for x in my_asset.get_size()]
        render_x = self.position[0] - player_position[0]
        render_y = player_position[1] - self.position[1]
        to_render = pygame.transform.scale(my_asset, (x * 2, y * 2))
        screen.blit(pygame.transform.flip(to_render, self.direction < 0, False), (render_x + half_screen_x + x, render_y + half_screen_y - y))
        if time.time() > self.time_destroyed:
            return True
        return False

class player:
    def __init__(self, username, room):
        self.username = username
        self.current_room_id = room
        self.current_room = load_room(self.current_room_id, 0)
        self.start_time = time.time()
        
        self.size = [14 * tilescale, 30 * tilescale]
        self.velocity = [0, 0]
        self.position = add_vectors(calculate_player_position_at_tile(self.current_room.spawn_tile), (self.size[0] / 2, 0))
        self.friction = 0.26
        self.grounded = False
        self.is_tile_above = False
        self.crouching = False
        self.can_stand_up = True
        self.holding_right_wall = False
        self.holding_left_wall = False
        self.jump_height = 30
        self.direction = 1
        self.dashing = False
        self.dash_timer = 0
        self.dash_power = 30
        self.dash_time = 0.2
        self.can_dash = False
        self.wings_not_used = True
        self.active_particles = []
        self.wall_no_clip = False
        self.wall_no_clip_stop_timestamp = 0
        self.is_standing_on_dash_pad = False

        self.recording = False
        self.recording_array = []
        
        self.dash_unlocked = True
        self.crouch_unlocked = True
        self.wall_jump_unlocked = True
        self.replay_end_offset = 0

        self.replaying = False

    def calculate_tile_index_at_player_location(self, horizontal_expansion, vertical_shift, vertical_index_shift):
        return [[x[0] - vertical_index_shift, x[1]] for x in [calculate_tile_index_at_position(add_vectors((self.position[0] - self.size[0] / 2 - horizontal_expansion, self.position[1] + vertical_shift), (0, -self.size[1]/2))), calculate_tile_index_at_position(add_vectors((self.position[0] - self.size[0] / 2  + horizontal_expansion, self.position[1] + vertical_shift), (self.size[0], -self.size[1]/2)))]]

    def loop(self, dt, space_pressed, semicolon_pressed, apostrophe_pressed, r_pressed, f_pressed):
        self.inputs(dt / 1000, space_pressed, semicolon_pressed, apostrophe_pressed, r_pressed, f_pressed)
        try: 
            if self.replay_end_offset == 0: self.physics()
        except: pass
        self.current_room.render(self.position)
        self.render(dt)
        to_remove = []
        for particle in self.active_particles:
            if particle.physics(self.position):
                to_remove.append(particle)
        for particle in to_remove:
            self.active_particles.remove(particle)

    def inputs(self, dt, space_pressed, semicolon_pressed, apostrophe_pressed, r_pressed, f_pressed):
        if self.replay_end_offset > 0: self.replay_end_offset -= 1
        else:
            if f_pressed:
                with open(GLOBAL_PATH + "gamefiles\\roomdata\\%s\\recording.txt" % self.current_room.numeric_id, "r") as textfile:
                    data = textfile.readlines()[0].strip("\n")
                    for position in data.split("|"):
                        clock.tick(120)
                        x, y = [float(x) for x in position.split(", ")[:2]]
                        is_crouching = position.split(", ")[2]
                        self.position = [x, y]
                        self.crouching = (is_crouching == "True")
                        self.current_room.render(self.position)
                        self.render(dt)
                        pygame.display.update()
                self.velocity = [0, 0]
                self.replay_end_offset = 5
            if r_pressed:
                if self.recording:
                    self.recording = False
                    recording_of_room = "|".join([", ".join([str(i) for i in x]) for x in self.recording_array])
                    with open(GLOBAL_PATH + "gamefiles\\roomdata\\%s\\recording.txt" % self.current_room.numeric_id, "w") as textfile:
                        textfile.write(recording_of_room)
                else:
                    self.recording_array = []
                    self.recording = True
            if self.grounded:
                self.wings_not_used = True
            scale = tilescale / 5
            keys = pygame.key.get_pressed()
            axis_of_movement = (keys[pygame.K_d] * scale * dt * 60 - keys[pygame.K_a] * scale * dt * 60,
                                keys[pygame.K_w] * scale * dt * 60 - keys[pygame.K_s] * scale * dt * 60)
            if axis_of_movement[0] != 0 and not self.dashing: self.direction = axis_of_movement[0]
            if not self.dashing: self.velocity = add_vectors(self.velocity, (axis_of_movement[0], 0))
            if not self.dashing: self.velocity[1] -= scale * dt * 60
            if self.can_stand_up: self.crouching = False
            if self.grounded:
                self.can_dash = True
                if space_pressed and not self.is_tile_above and not self.crouching:
                    self.velocity[1] += self.jump_height * scale * 0.75
                if keys[pygame.K_LSHIFT] and self.crouch_unlocked:
                    self.crouching = True
            if (self.grounded or (self.wings_not_used and not self.grounded)) and (space_pressed and not self.is_tile_above and not self.crouching):
                    self.velocity[1] = self.jump_height * scale * 0.75
                    if not self.grounded:
                        self.wings_not_used = False
                        self.can_dash = True

            if not self.wall_no_clip:
                if self.holding_left_wall or self.holding_right_wall:
                    self.wings_not_used = True
                    if self.velocity[1] < -4 * scale:
                        self.velocity[1] = -4 * scale

            left_scale = 1
            right_scale = 1

            if keys[pygame.K_a]:
                left_scale = 0.5
            if keys[pygame.K_d]:
                right_scale = 0.5

            if not self.wall_no_clip:
                if self.holding_left_wall:
                    self.direction = 1
                    if space_pressed and not self.grounded:
                        self.velocity[0] = self.jump_height * scale * 1 * left_scale
                        self.velocity[1] = self.jump_height * scale * 1.1

                if self.holding_right_wall:
                    self.direction = -1
                    if space_pressed and not self.grounded:
                        self.velocity[0] = -self.jump_height * scale * 1 * right_scale
                        self.velocity[1] = self.jump_height * scale * 1.1

            if self.dash_unlocked:
                if apostrophe_pressed and self.can_dash:
                    if self.is_standing_on_dash_pad:
                        self.wall_no_clip_stop_timestamp = time.time() + self.dash_time
                        self.wall_no_clip = True
                    self.can_dash = False
                    self.dashing = True
                    self.dash_timer = 0
                    self.active_particles.append(particle("dash_cloud", self.dash_time, self.position, isGravity=False, velocity=[-10 * self.direction, 0], direction=self.direction * -1))

            if self.dashing:
                self.velocity = [60 * dt * self.dash_power * self.direction, 0]
                self.dash_timer += dt
            
            if self.dash_timer > self.dash_time:
                self.dashing = False
                self.dash_timer = 0

            if self.can_stand_up:
                if not self.grounded:
                    self.crouching = False

            self.wall_no_clip = time.time() < self.wall_no_clip_stop_timestamp

    def die(self):
        self.velocity = [0, 0]
        self.position = add_vectors(calculate_player_position_at_tile(self.current_room.spawn_tile), (self.size[0] / 2, 0))
        self.dashing = False
        self.crouching = False

    def new_physics(self):

        self.position = add_vectors(self.position, self.velocity)
        if not self.dashing:
            self.velocity[0] *= (1 - self.friction)

        #Starter values
        if not self.dashing: self.can_stand_up = True
        self.grounded = False

        #Find relevant tile indices
        tiles_under_feet = self.calculate_tile_index_at_player_location(-1, 0, 0)
        tiles_in_feet = self.calculate_tile_index_at_player_location(-1, 0, 1)
        tiles_in_head = self.calculate_tile_index_at_player_location(-1, tilescale, 1)
        tiles_above_head = self.calculate_tile_index_at_player_location(-tilescale, tilescale / 2.5, 2)

        spikes_under_feet = self.calculate_tile_index_at_player_location(-tilescale, -tilescale, 0)
        spikes_in_feet = self.calculate_tile_index_at_player_location(-tilescale, 0, 0)   
        spikes_in_head = self.calculate_tile_index_at_player_location(-tilescale, 0, 0)   
        spikes_above_head = self.calculate_tile_index_at_player_location(-tilescale, tilescale, 0)   


        #Ground check, friction check.
        self.friction = 0
        for y, x in tiles_under_feet:
            tile = self.current_room.room_array[y][x]
            self.friction += tile.friction
            if tile.collide and self.velocity[1] < 0: 
                self.position[1] = calculate_player_position_at_tile([x, y])[1] + 16 * tilescale
                self.velocity[1] = 0
                self.grounded = True
        self.friction /= 2
            
        #Check for blocks above head.
        self.is_tile_above = False
        for y, x in tiles_above_head:
            tile = self.current_room.room_array[y][x]
            pos_x = half_screen_x - self.size[0] / 2
            pos_y = half_screen_y - self.size[1]
            position = calculate_player_position_at_tile([x, y])
            x_position = (x * 16 * tilescale) - self.position[0]
            y_position = (y * 16 * tilescale) + self.position[1]
            pygame.draw.rect(screen, (0, 0, 255), pygame.Rect(x_position + half_screen_x, y_position + half_screen_y, 16 * tilescale, 16 * tilescale))
            self.friction += tile.friction
            if tile.collide:
                self.is_tile_above = True
            if y_position + half_screen_y > pos_y and tile.collide and self.velocity[1] > 0:
                self.position[1] = calculate_player_position_at_tile([x, y])[1] - tilescale * 16 * 2
                self.velocity[1] = 0

        #Check if the player can stand up when crouching.
        if self.crouching and not self.dashing:
            for y, x in tiles_above_head:
                tile = self.current_room.room_array[y][x]
                if tile.collide:
                    self.can_stand_up = False

        #Check for foot high walls.
        for y, x in tiles_in_feet:
            x_position = (x * 16 * tilescale) - self.position[0]
            y_position = (y * 16 * tilescale) + self.position[1]
            pygame.draw.rect(screen, (0, 0, 255), pygame.Rect(x_position + half_screen_x, y_position + half_screen_y, 16 * tilescale, 16 * tilescale))
        ly, lx = tiles_in_feet[0]
        ry, rx = tiles_in_feet[1]
        left_tile = self.current_room.room_array[ly][lx]
        right_tile = self.current_room.room_array[ry][rx]
        if left_tile.collide:
            self.position[0] = calculate_player_position_at_tile([lx, ly])[0] + 16 * tilescale + self.size[0] / 2
        if right_tile.collide:
            self.position[0] = calculate_player_position_at_tile([rx, ry])[0] - self.size[0] / 2

        #Check for head high walls.
        if not self.crouching:
            for y, x in tiles_in_head:
                x_position = (x * 16 * tilescale) - self.position[0]
                y_position = (y * 16 * tilescale) + self.position[1]
                pygame.draw.rect(screen, (0, 255, 255), pygame.Rect(x_position + half_screen_x, y_position + half_screen_y, 16 * tilescale, 16 * tilescale))
            ly, lx = tiles_in_head[0]   
            ry, rx = tiles_in_head[1]
            left_tile = self.current_room.room_array[ly][lx]
            right_tile = self.current_room.room_array[ry][rx]
            if left_tile.collide:
                self.position[0] = calculate_player_position_at_tile([lx, ly])[0] + 16 * tilescale + self.size[0] / 2
            if right_tile.collide:
                self.position[0] = calculate_player_position_at_tile([rx, ry])[0] - self.size[0] / 2

    def physics(self):
        self.can_stand_up = True
        self.position = add_vectors(self.position, self.velocity)
        if not self.dashing:self.velocity[0] *= (1 - self.friction)
        tiles_under_feet = []
        tiles_under_feet.append(calculate_tile_index_at_position(add_vectors((self.position[0] - self.size[0] / 2 + tilescale, self.position[1]), (0, -self.size[1]/2))))
        tiles_under_feet.append(calculate_tile_index_at_position(add_vectors((self.position[0] - self.size[0] / 2 - tilescale, self.position[1]), (self.size[0], -self.size[1]/2))))
        tiles_above_head = []
        tiles_above_head.append(calculate_tile_index_at_position(add_vectors((self.position[0] - self.size[0] / 2 + tilescale, self.position[1] + 2), (0, -self.size[1]/2))))
        tiles_above_head.append(calculate_tile_index_at_position(add_vectors((self.position[0] - self.size[0] / 2 - tilescale, self.position[1] + 2), (self.size[0], -self.size[1]/2))))
        foot_level = []
        if self.grounded:
            foot_level.append(calculate_tile_index_at_position(add_vectors((self.position[0] - self.size[0] / 2, self.position[1]), (0, -self.size[1]/2))))
            foot_level.append(calculate_tile_index_at_position(add_vectors((self.position[0] - self.size[0] / 2, self.position[1]), (self.size[0], -self.size[1]/2))))
        else:
            foot_level.append(calculate_tile_index_at_position(add_vectors((self.position[0] - self.size[0] / 2, self.position[1] - tilescale * 8), (0, -self.size[1]/2))))
            foot_level.append(calculate_tile_index_at_position(add_vectors((self.position[0] - self.size[0] / 2, self.position[1] - tilescale * 8), (self.size[0], -self.size[1]/2))))
        foot_level = [[x[0] - 1, x[1]] for x in foot_level]
        head_level = []
        head_level.append(calculate_tile_index_at_position(add_vectors((self.position[0] - self.size[0] / 2, self.position[1] - tilescale), (0, -self.size[1]/2))))
        head_level.append(calculate_tile_index_at_position(add_vectors((self.position[0] - self.size[0] / 2, self.position[1] - tilescale), (self.size[0], -self.size[1]/2))))
        head_level = [[x[0] - 2, x[1]] for x in head_level]
        wall_trigger = []
        wall_trigger.append(calculate_tile_index_at_position(add_vectors((self.position[0] - self.size[0] / 2 - tilescale, self.position[1] - tilescale), (0, -self.size[1]/2))))
        wall_trigger.append(calculate_tile_index_at_position(add_vectors((self.position[0] - self.size[0] / 2 + tilescale, self.position[1] - tilescale), (self.size[0], -self.size[1]/2))))
        wall_trigger = [[x[0] - 1, x[1]] for x in wall_trigger]
        self.grounded = False
        self.is_standing_on_dash_pad = False
        temp_friction = 0
        for y, x in tiles_under_feet:
            if self.current_room.room_array[y][x].collide and self.velocity[1] < 0:
                self.velocity[1] = 0
                self.position[1] = calculate_player_position_at_tile((x, y))[1] + self.size[1] / 2
                self.grounded = True
            if self.current_room.room_array[y][x].numeric_id == 9:
                self.is_standing_on_dash_pad = True
            temp_friction += self.current_room.room_array[y][x].friction
        self.friction = temp_friction / 2
        if y < 0:
            self.grounded = False
        self.is_tile_above = False
        for y, x in tiles_above_head:
            if self.current_room.room_array[y-2][x].collide and not self.current_room.room_array[y-2][x].kill_player:
                if self.velocity[1] > 0: 
                    self.velocity[1] = 0
                    self.position[1] = calculate_player_position_at_tile((x, y-2))[1] - self.size[1]
                self.is_tile_above = True
        foot_level = []
        if self.grounded:
            foot_level.append(calculate_tile_index_at_position(add_vectors((self.position[0] - self.size[0] / 2, self.position[1]), (0, -self.size[1]/2))))
            foot_level.append(calculate_tile_index_at_position(add_vectors((self.position[0] - self.size[0] / 2, self.position[1]), (self.size[0], -self.size[1]/2))))
        else:
            foot_level.append(calculate_tile_index_at_position(add_vectors((self.position[0] - self.size[0] / 2, self.position[1] - tilescale * 8), (0, -self.size[1]/2))))
            foot_level.append(calculate_tile_index_at_position(add_vectors((self.position[0] - self.size[0] / 2, self.position[1] - tilescale * 8), (self.size[0], -self.size[1]/2))))
        foot_level = [[x[0] - 1, x[1]] for x in foot_level]
        head_level = []
        head_level.append(calculate_tile_index_at_position(add_vectors((self.position[0] - self.size[0] / 2, self.position[1] + tilescale * 8), (0, -self.size[1]/2))))
        head_level.append(calculate_tile_index_at_position(add_vectors((self.position[0] - self.size[0] / 2, self.position[1] + tilescale * 8), (self.size[0], -self.size[1]/2))))
        head_level = [[x[0] - 1, x[1]] for x in head_level]
        wall_trigger = []
        wall_trigger.append(calculate_tile_index_at_position(add_vectors((self.position[0] - self.size[0] / 2 - tilescale, self.position[1] - tilescale), (0, -self.size[1]/2))))
        wall_trigger.append(calculate_tile_index_at_position(add_vectors((self.position[0] - self.size[0] / 2 + tilescale, self.position[1] - tilescale), (self.size[0], -self.size[1]/2))))
        wall_trigger = [[x[0] - 1, x[1]] for x in wall_trigger]
        if not self.wall_no_clip:
            uly, ulx = head_level[0]
            if self.current_room.room_array[uly][ulx].collide:
                self.can_stand_up = False
                if not self.crouching:
                    self.velocity[0] = 0
                    self.position[0] = calculate_player_position_at_tile((ulx, uly))[0] + tilescale * 16 + self.size[0] / 2
            if self.current_room.room_array[uly][ulx].kill_player:
                self.can_stand_up = False
            self.friction = temp_friction / 2
            ury, urx = head_level[1]
            if self.current_room.room_array[ury][urx].collide:
                self.can_stand_up = False
                if not self.crouching:
                    self.velocity[0] = 0
                    self.position[0] = calculate_player_position_at_tile((urx, ury))[0] - self.size[0] / 2
            if self.current_room.room_array[ury][urx].kill_player: 
                self.can_stand_up = False
            self.friction = temp_friction / 2   
            lly, llx = foot_level[0]
            if self.current_room.room_array[lly][llx].collide:
                self.velocity[0] = 0
                self.position[0] = calculate_player_position_at_tile((llx, lly))[0] + tilescale * 16 + self.size[0] / 2
            if self.current_room.room_array[lly][llx].kill_player:
                self.dashing = False
            self.friction = temp_friction / 2
            lry, lrx = foot_level[1]
            if self.current_room.room_array[lry][lrx].collide:
                self.velocity[0] = 0
                self.position[0] = calculate_player_position_at_tile((lrx, lry))[0] - self.size[0] / 2
            if self.current_room.room_array[lry][lrx].kill_player:
                self.dashing = False
            level_change = 0
        for y, x in foot_level:
            if self.current_room.room_array[y][x].numeric_id == 6:
                level_change = -1
            if self.current_room.room_array[y][x].numeric_id == 7:
                level_change = 1
        for y, x in head_level:
            if self.current_room.room_array[y][x].numeric_id == 6:
                level_change = -1
            if self.current_room.room_array[y][x].numeric_id == 7:
                level_change = 1
        if level_change != 0: 
            screen.fill((0, 0, 0))
            text = font.render("LOADING...", True, (255,255,255), (0,0,0))
            screen.blit(text, (10, 10))
            pygame.display.update()
            self.recording = False
            self.recording_array = []
            self.current_room = load_room(self.current_room.numeric_id + level_change, ( 1 - int(level_change + 1) / 2))
            self.die()
        else:
            self.friction = temp_friction / 2
            self.collided_left = False
            lly, llx = wall_trigger[0]
            if self.current_room.room_array[lly][llx].collide:
                self.collided_left = True
            self.collided_right = False
            lry, lrx = wall_trigger[1]
            if self.current_room.room_array[lry][lrx].collide:
                self.collided_right = True
            if self.collided_left and not self.grounded and self.wall_jump_unlocked:
                self.holding_left_wall = True
            else: self.holding_left_wall = False
            if self.collided_right and not self.grounded and self.wall_jump_unlocked:
                self.holding_right_wall = True
            else: self.holding_right_wall = False
            if self.holding_left_wall or self.holding_right_wall:
                self.dashing = False
                self.can_dash = True      
                self.wings_not_used = True
            if self.dashing:
                self.can_stand_up = False  
            death = []
            dash_scale = 1
            if self.dashing:
                dash_scale = 3
            death.append(calculate_tile_index_at_position(add_vectors((self.position[0] - self.size[0] / 2 + tilescale * dash_scale, self.position[1] - tilescale / 1), (0, -self.size[1]/2))))
            death.append(calculate_tile_index_at_position(add_vectors((self.position[0] - self.size[0] / 2 - tilescale * dash_scale, self.position[1] - tilescale / 1), (self.size[0], -self.size[1]/2))))
            death.append(calculate_tile_index_at_position(add_vectors((self.position[0] - self.size[0] / 2 + tilescale * dash_scale, self.position[1]), (0, -self.size[1]/2))))
            death.append(calculate_tile_index_at_position(add_vectors((self.position[0] - self.size[0] / 2 - tilescale * dash_scale, self.position[1]), (self.size[0], -self.size[1]/2))))
            death = [[death[x][0] - 2, death[x][1]] if x < 2 else [death[x][0] - 1, death[x][1]] for x in range(len(death))]
            if not self.dashing:
                count = 0
                for y, x in death:
                    if count < 2:
                        if self.current_room.room_array[y][x].kill_player and not self.crouching:
                            self.die()
                    else:
                        if self.current_room.room_array[y][x].kill_player:
                            self.die()
                    count += 1

        if self.recording:
            self.recording_array.append([self.position[0], self.position[1], self.crouching])
        

    def render(self, dt):
        pos_x = half_screen_x - self.size[0] / 2
        pos_y = half_screen_y - self.size[1] / 2
        colour = (255, 0, 0)
        if not self.crouching: pygame.draw.rect(screen, colour, pygame.Rect(pos_x, pos_y, self.size[0], self.size[1]))
        else: pygame.draw.rect(screen, colour, pygame.Rect(pos_x, pos_y + self.size[1] / 2, self.size[0], self.size[1] / 2))
        text = font.render("LEVEL %s" % self.current_room.numeric_id, True, (255,255,255), self.current_room.colour)
        screen.blit(text, (10, 10))
        text = font.render("%s FPS" % round(1000 / dt), True, (255,255,255), self.current_room.colour)
        screen.blit(text, (2 * half_screen_x - 100, 10))
        text = font.render("%s" % round(time.time() - self.start_time, 2), True, (255, 255, 255), self.current_room.colour)
        screen.blit(text, (half_screen_x, 1000))
        text = font.render(", ".join([str(round(x, 2)) for x in self.position]), True, (255, 255, 255), self.current_room.colour)
        screen.blit(text, (1600, 1000))

class room:
    def __init__(self, room_array, name, numeric_id, spawn_tile, colour):
        self.room_array = []
        for row in room_array:
            self.room_array.append([tile(int(numeric_id)) for numeric_id in row])
        self.name = name
        self.numeric_id = numeric_id
        self.spawn_tile = [int(x) for x in spawn_tile]
        self.colour = colour

    def render(self, position):
        player_x, player_y = position
        y, x = calculate_floor_tile_index_at_position(position)
        blocks_on_either_side_x = int(half_screen_x / (16 * tilescale)) + 2
        blocks_on_either_side_y = int(half_screen_y / (16 * tilescale)) + 2
        start_x = 0
        end_x = len(self.room_array[0])
        start_y = 0
        end_y = len(self.room_array)
        if x - blocks_on_either_side_x > 0:
            start_x = x - blocks_on_either_side_x
        if x + blocks_on_either_side_x < len(self.room_array) - 1:
            end_x = x + blocks_on_either_side_x
        if y - blocks_on_either_side_y > 0:
            start_y = y - blocks_on_either_side_y
        if y + blocks_on_either_side_y < len(self.room_array) - 1:
            end_y = y + blocks_on_either_side_y
        player_depth = pygame.Surface((1920, 1080))
        player_depth.fill(self.colour)
        for row in range(start_y, end_y):
            for tile in range(start_x, end_x):
                x_position = (tile * 16 * tilescale) - player_x
                y_position = (row * 16 * tilescale) + player_y
                if self.room_array[row][tile].render:
                    asset_index = self.room_array[row][tile].numeric_id
                    asset = tile_assets[asset_index]
                    if self.room_array[row][tile].name == "dirt" and row > 0:
                        if self.room_array[row - 1][tile].name == "air":
                            asset = grass_asset
                    player_depth.blit(asset, (x_position + half_screen_x, y_position + half_screen_y))
        screen.blit(player_depth, (0, 0))
                
class tile:
    def __init__(self, numeric_id):
        self.numeric_id = numeric_id
        with open(GLOBAL_PATH + "gamefiles\\tiledatabyID.txt", "r") as tiledata:
            data = [x.strip("\n") for x in tiledata.readlines()][numeric_id + 1].split(" ")
            num = int(data[0])
            self.friction = float(data[1])
            self.allow_wall_jump, self.kill_player, self.render, self.collide = [bool(int(x)) for x in data[2:]]
        with open(GLOBAL_PATH + "gamefiles\\tilemapIDs.txt", "r") as tilemapIDs:
            self.name = tilemapIDs.readlines()[self.numeric_id].strip("\n").split(" ")[1]

def load_room(numeric_id, entry_point):
    with open(GLOBAL_PATH + "gamefiles\\roomdata\\%s\\roominfo.txt" % numeric_id, "r") as roominfo:
        lines = roominfo.readlines()
        room_name = lines[0].strip("\n")
        spawn_tile = lines[1 + int(entry_point)].strip("\n").split(", ")
        colour = [int(x) for x in lines[3].strip("\n").split(", ")]
    with open(GLOBAL_PATH + "gamefiles\\roomdata\\%s\\tilemap.txt" % numeric_id, "r") as tilemap:
        room_tile_map = [row.strip("\n") for row in tilemap.readlines()]
    return room(room_tile_map, room_name, numeric_id, spawn_tile, colour)

tile_assets = load_tiles()
grass_asset = pygame.transform.scale(pygame.image.load("assets\\tiles\\grass.png").convert_alpha(), (16 * tilescale, 16 * tilescale))
tile_assets = scale_all_tiles(tilescale, tile_assets)
running = True
timeparadox = player("TIMEPARADOX", 1)

while running:
    dt = clock.tick(60)
    is_space_pressed = False
    semicolon_pressed = False
    apostrophe_pressed = False
    r_pressed = False
    f_pressed = False
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_i and tilescale < 10: 
                tilescale += 1
                timeparadox.position[0] /= (tilescale - 1)
                timeparadox.position[0] *= tilescale
                timeparadox.position[1] /= (tilescale - 1)
                timeparadox.position[1] *= tilescale
                timeparadox.size[0] /= (tilescale - 1)
                timeparadox.size[0] *= tilescale
                timeparadox.size[1] /= (tilescale - 1)
                timeparadox.size[1] *= tilescale
                tile_assets = scale_all_tiles(tilescale, tile_assets)
                grass_asset = pygame.transform.scale(pygame.image.load("assets\\tiles\\grass.png").convert_alpha(), (16 * tilescale, 16 * tilescale))
            if event.key == pygame.K_o and tilescale > 4:
                tilescale -= 1
                timeparadox.position[0] /= (tilescale + 1)
                timeparadox.position[0] *= tilescale
                timeparadox.position[1] /= (tilescale + 1)
                timeparadox.position[1] *= tilescale
                timeparadox.size[0] /= (tilescale + 1)
                timeparadox.size[0] *= tilescale
                timeparadox.size[1] /= (tilescale + 1)
                timeparadox.size[1] *= tilescale
                tile_assets = scale_all_tiles(tilescale, tile_assets)
                grass_asset = pygame.transform.scale(pygame.image.load("assets\\tiles\\grass.png").convert_alpha(), (16 * tilescale, 16 * tilescale))
            if event.key == pygame.K_SPACE:
                is_space_pressed = True
            if event.key == pygame.K_SEMICOLON:
                semicolon_pressed = True
            if int(event.key) == 39:
                apostrophe_pressed = True
            if event.key == pygame.K_r:
                r_pressed = True
            if event.key == pygame.K_f:
                f_pressed = True
        if event.type == pygame.QUIT:
            running = False
    timeparadox.loop(dt, is_space_pressed, semicolon_pressed, apostrophe_pressed, r_pressed, f_pressed)
    pygame.display.flip()
    screen.fill((255, 255, 255))
