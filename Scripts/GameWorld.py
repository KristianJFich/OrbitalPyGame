import pygame
import os
import PrefabCreator
from FontManager.fontmanager import FontManager
from Scripts.GameObject import Layers
from SoundManager.soundmanager import SoundManager
import globals
from DesignPatterns.StatePattern import StateMachine
from GameObjectCreator import GameObjectFactory, GameObjectBuilder
from GameStates.SubGameStates import PlayGameState, MenuGameState
from Scripts.Spawner import Spawner
from Scripts.animation import Animation


class GameWorld:
    def __init__(self, width, height, caption):
        self.render_layers = [[] for _ in range(len(Layers))]
        globals.soundManager = SoundManager()
        globals.soundManager.play_music("menu")

        self.menu_game_state = None
        self.play_game_state = None
        self.stateMachine = None
        self.width = width
        self.height = height
        self.caption = caption
        self.gameobjects = []
        self.colliding_gameobjects = []
        self.go_to_remove = []
        self.clock = pygame.time.Clock()
        self.delta_time = None
        self.project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
        self.prefab_base_dir = os.path.join(self.project_dir, "Content", "Prefabs", "Base")
        self.InitializeStates()

        pygame.init()
        globals.fontManager = FontManager(os.path.join(self.project_dir, "FontManager", "Fonts", "Arcade.TTF"))
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(self.caption)

    def initialize_player(self):

        # Get where the player prefab should be located
        player_prefab_dir = os.path.join(self.prefab_base_dir, "prefab_base_player.pya")

        # Checks if there is a save file on player. If there is use that instead!
        # if not os.path.exists(player_prefab_dir):
        #     print("No file found: Creating new player!")
        #     player_image_path = os.path.join(self.project_dir, "Content", "Player", "player.png")
        #     go_player = GameObjectFactory.build_base(x=300, y=400, image_path=player_image_path, world=self)
        # 
        #     GameObjectBuilder.add_rigidbody(go=go_player,
        #                                     acceleration=(350, 150),
        #                                     friction=(200, 200),
        #                                     max_speed=(350, 250)
        #                                     )
        # 
        #     GameObjectBuilder.add_player(go=go_player)
        #     idle_image_path = os.path.join(self.project_dir, "Content", "Player", "Idle.png")
        #     boost_image_path = os.path.join(self.project_dir, "Content", "Player", "Boost.png")
        #     animations_list = [Animation("idle", idle_image_path, 1, 1, ),
        #                        Animation("boost", boost_image_path, 5, .1, )]
        #     GameObjectBuilder.add_animator(animations_list, go=go_player)
        # 
        #     PrefabCreator.create_prefab_instance(go=go_player, go_name="player", prefab_file_path=player_prefab_dir)
        # else:
        #     print("File found: Creating player from file!")
        #     go_player = PrefabCreator.load_prefab_instance(file_path=player_prefab_dir, world=self)

        player_image_path = os.path.join(self.project_dir, "Content", "Player", "player.png")
        go_player = GameObjectFactory.build_base(x=600, y=600, image_path=player_image_path, world=self,
                                                 layer=Layers.FOREGROUND, tag="Player")

        GameObjectBuilder.add_rigidbody(go=go_player,
                                        acceleration=(350, 150),
                                        friction=(200, 200),
                                        max_speed=(350, 250)
                                        )
        
        GameObjectBuilder.add_collision_handler(go=go_player)
        GameObjectBuilder.add_player(go=go_player)
        idle_image_path = os.path.join(self.project_dir, "Content", "Player", "Idle.png")
        boost_image_path = os.path.join(self.project_dir, "Content", "Player", "Boost.png")
        animations_list = [Animation("idle", idle_image_path, 1, 1, ),
                           Animation("boost", boost_image_path, 5, .1, )]
        GameObjectBuilder.add_animator(animations_list, go=go_player)
        self.instantiate_go(go=go_player)

    def initialize_spawner(self):
        spawner = Spawner
        spawner.__init__(self)

    def instantiate_go(self, go):
        self.render_layers[go.layer.value].append(go)
        self.gameobjects.append(go)

    def destroy_go(self, go):
        self.go_to_remove.append(go)

    def _clear_removed_objects(self):
        for go in self.go_to_remove:
            if self.render_layers[go.layer.value].__contains__(go):
                self.render_layers[go.layer.value].remove(go)
            if self.gameobjects.__contains__(go):
                self.gameobjects.remove(go)
            self.go_to_remove.remove(go)

    def update(self):
        self.delta_time = self.clock.tick(60) / 1000.0

        # Update all game objects
        for layer in self.render_layers:
            for go in layer:
                go.update()
        
        # Handle collision between two gameobjects
        for go1 in self.gameobjects:
            for go2 in self.gameobjects:
                if go1.tag != go2.tag:
                    if go1.transform.rect.colliderect(go2.transform.rect):
                        if (go1, go2) not in self.colliding_gameobjects:
                            # Objects have just started colliding
                            go1.handle_collision(go2, "enter")
                            go2.handle_collision(go1, "enter")
                            self.colliding_gameobjects.append((go1, go2))
                        else:
                            # Objects are still colliding
                            go1.handle_collision(go2, "stay")
                            go2.handle_collision(go1, "stay")
                    elif (go1, go2) in self.colliding_gameobjects:
                        # Objects have stopped colliding
                        go1.handle_collision(go2, "exit")
                        go2.handle_collision(go1, "exit")
                        self.colliding_gameobjects.remove((go1, go2))

        # Remove any game objects that have been destroyed
        self._clear_removed_objects()

    def draw(self):

        self.screen.fill((255, 255, 255))
        globals.fontManager.render_font(f"Score:{globals.score}", (50, 50), self.screen, "black")

        for layer in self.render_layers:
            for go in layer:
                go.draw(self.screen)
                pygame.draw.rect(surface=self.screen, color=go.collision_color,
                                 rect=go.transform.rect, width=3)

        pygame.display.flip()

    def start(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            self.update()
            self.draw()

        pygame.quit()

    def InitializeStates(self):
        self.stateMachine = StateMachine()
        self.play_game_state = PlayGameState(self, self.stateMachine)
        self.menu_game_state = MenuGameState(self, self.stateMachine)
        self.stateMachine.start_statemachine(self.play_game_state)
