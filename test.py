from ursina import *
import random
from textwrap import dedent

# Declare game_instance as a global variable
game_instance = None

class Game:
    def __init__(self):
        global game_instance  # Declare it as global to access outside this class
        game_instance = self  # Assign self to the global variable
        app = Ursina(size=(1280, 720))  # Set your desired window size here
        self.setup_scene()  # Set up the scene
        self.model, self.texture = 'models/custom_cube', 'textures/rubik_texture'
        self.load_game()  # Load game elements
        self.create_buttons()  # Create action buttons for rotating the cube
        app.run()  # Start the Ursina application

    def setup_scene(self):
        # Create ground plane and sky
        Entity(model='quad', scale=60, texture='white_cube', texture_scale=(60, 60), rotation_x=90, y=-5,
                color=color.light_gray)  # Ground Plane
        Entity(model='sphere', scale=100, texture='textures/sky0', double_sided=True)  # Sky
        EditorCamera()
        camera.world_position = (0, 0, -15)

    def load_game(self):
        self.create_cube_positions()  # Create positions for cube sides
        self.CUBES = [Entity(model=self.model, texture=self.texture, position=pos) for pos in self.SIDE_POSITIONS]

        self.PARENT = Entity()  # Parent entity for rotations
        self.rotation_axes = {'LEFT': 'x', 'RIGHT': 'x', 'TOP': 'y', 'BOTTOM': 'y', 'FACE': 'z', 'BACK': 'z'}

        self.cubes_side_positions = {
            'LEFT': self.LEFT,
            'BOTTOM': self.BOTTOM,
            'RIGHT': self.RIGHT,
            'FACE': self.FACE,
            'BACK': self.BACK,
            'TOP': self.TOP
        }

        self.animation_time = 0.5  # Duration for rotation animations
        self.action_trigger = True
        self.action_mode = True
        self.message = Text(origin=(0, 19), color=color.black)

        self.toggle_game_mode()
        self.create_sensors()
        self.random_state(rotations=3)  # Initial state of the cube

    def create_buttons(self):
        '''Create buttons for each side rotation'''
        button_width = 0.1
        button_height = 0.05

        # Create buttons and assign actions to them
        button_names = ['LEFT', 'RIGHT', 'TOP', 'BOTTOM', 'FACE', 'BACK']
        for i, name in enumerate(button_names):
            button = Button(text=name, position=(-0.9 + i * button_width, -0.8),
                            scale=(button_width, button_height),
                            color=color.azure,
                            on_click=lambda b=name: self.rotate_side(b))
            button.tooltip = f'Rotate {name} side'

    def random_state(self, rotations=3):
        # Randomly rotate sides to create an initial shuffled state
        [self.rotate_side_without_animation(random.choice(list(self.rotation_axes))) for _ in range(rotations)]

    def rotate_side_without_animation(self, side_name):
        cube_positions = self.cubes_side_positions[side_name]
        rotation_axis = self.rotation_axes[side_name]
        self.reparent_to_scene()  # Reparent to allow rotation
        for cube in self.CUBES:
            if cube.position in cube_positions:
                cube.parent = self.PARENT
                setattr(self.PARENT, f'rotation_{rotation_axis}', getattr(self.PARENT, f'rotation_{rotation_axis}') + 90)

    def create_sensors(self):
        '''Create invisible sensors for detecting collisions with mouse clicks'''
        create_sensor = lambda name, pos, scale: Entity(name=name, position=pos,
                                                        model='cube', color=color.dark_gray,
                                                        scale=scale,
                                                        collider='box',
                                                        visible=False)

        # Define sensors for each side of the cube
        self.LEFT_sensor = create_sensor(name='LEFT', pos=(-0.99, 0, 0), scale=(1.01, 3.01, 3.01))
        self.FACE_sensor = create_sensor(name='FACE', pos=(0, 0, -0.99), scale=(3.01, 3.01, 1.01))
        self.BACK_sensor = create_sensor(name='BACK', pos=(0, 0, 0.99), scale=(3.01, 3.01, 1.01))
        self.RIGHT_sensor = create_sensor(name='RIGHT', pos=(0.99, 0, 0), scale=(1.01, 3.01, 3.01))
        self.TOP_sensor = create_sensor(name='TOP', pos=(0, 1, 0), scale=(3.01, 1.01, 3.01))
        self.BOTTOM_sensor = create_sensor(name='BOTTOM', pos=(0, -1, 0), scale=(3.01, 1.01, 3.01))

    def toggle_game_mode(self):
        '''Switching view mode or interacting with Rubik's Cube'''
        self.action_mode = not self.action_mode
        msg = dedent(f"{'ACTION mode ON' if self.action_mode else 'VIEW mode ON'}"
                     f" (to switch - press 'g')").strip()
        self.message.text = msg
        print(f"Mode changed to: {msg}")  # Debug print

    def toggle_animation_trigger(self):
        '''Prohibiting side rotation during rotation animation'''
        self.action_trigger = not self.action_trigger

    def rotate_side(self, side_name):
        '''Rotate the specified side of the cube'''
        if not self.action_trigger:
            return

        self.toggle_animation_trigger()

        cube_positions = self.cubes_side_positions[side_name]
        rotation_axis = self.rotation_axes[side_name]
        self.reparent_to_scene()  # Reparent to allow rotation
        for cube in self.CUBES:
            if cube.position in cube_positions:
                cube.parent = self.PARENT
                # Animate rotation of the parent entity
                getattr(self.PARENT.animate_rotation_, f'{rotation_axis}')(90, duration=self.animation_time)

        invoke(self.toggle_animation_trigger, delay=self.animation_time + 0.11)

    def reparent_to_scene(self):
        '''Reparent cubes back to the scene after rotation'''
        for cube in self.CUBES:
            if cube.parent == self.PARENT:
                world_pos = round(cube.world_position.x), round(cube.world_position.y), round(cube.world_position.z)
                world_rot = cube.world_rotation

                cube.parent = scene
                cube.position = world_pos
                cube.rotation = world_rot

        # Reset parent rotation after reparenting
        self.PARENT.rotation = Vec3(0)

    def create_cube_positions(self):
        '''Define positions for each side of the Rubik's Cube'''
        self.LEFT = {Vec3(-1, y, z) for y in range(-1, 2) for z in range(-1, 2)}
        self.BOTTOM = {Vec3(x, -1, z) for x in range(-1, 2) for z in range(-1, 2)}
        self.FACE = {Vec3(x, y, -1) for x in range(-1, 2) for y in range(-1, 2)}
        self.BACK = {Vec3(x, y, 1) for x in range(-1, 2) for y in range(-1, 2)}
        self.RIGHT = {Vec3(1, y, z) for y in range(-1, 2) for z in range(-1, 2)}
        self.TOP = {Vec3(x, 1, z) for x in range(-1, 2) for z in range(-1, 2)}

        # Combine all side positions into one set
        self.SIDE_POSITIONS = self.LEFT | self.BOTTOM | self.FACE | self.BACK | self.RIGHT | self.TOP


def input(key):
    global game_instance  # Declare game_instance as global to access the instance
    # Handle mouse input to rotate sides or toggle game mode
    if key in ('mouse1', 'mouse3') and game_instance.action_mode and game_instance.action_trigger:
        for hitinfo in mouse.collisions:
            collider_name = hitinfo.entity.name
            if (key == 'mouse1' and collider_name in ('LEFT', 'RIGHT', 'FACE', 'BACK')) or \
                    (key == 'mouse3' and collider_name in ('TOP', 'BOTTOM')):
                print(f"Rotating {collider_name}")
                game_instance.rotate_side(collider_name)
                break

    if key == 'g':  # Toggle game mode
        game_instance.toggle_game_mode()


if __name__ == "__main__":
    game_instance = Game()  # Initialize the game
