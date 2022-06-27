import pygame
import sys
from vector2D import Vector2D
from random import randint

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

GAME_OVER_EVENT = pygame.USEREVENT + 1


class Paddle(pygame.sprite.Sprite):

    instances = pygame.sprite.Group()

    def __init__(self, size=(32, 8), pos=(0, 0), origin="center"):
        super(Paddle, self).__init__()
        Paddle.instances.add(self)
        self.image = pygame.Surface(size)
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.__setattr__(origin, pos)
        self.circle = {"pos": (self.rect.width // 2, -int(self.rect.width * 1.9)), "radius": self.rect.width * 2}
        pygame.draw.circle(self.image, (100, 100, 100),  self.circle["pos"], self.circle["radius"])
        self.position = Vector2D(*self.rect.center)
        self.velocity_x = 0

    def border_collision(self, screen):
        if self.rect.right > screen.right:
            self.position.x = screen.right - self.rect.width // 2
            self.rect.center = self.position.x, self.position.y
            self.velocity_x = 0
        elif self.rect.left < screen.left:
            self.position.x = screen.left + self.rect.width // 2
            self.velocity_x = 0
            self.rect.center = self.position.x, self.position.y

    def update(self, screen, seconds, *ignored):
        self.position.x += self.velocity_x * seconds
        self.rect.center = self.position.x, self.position.y
        self.border_collision(screen)


class Block(pygame.sprite.Sprite):
    def __init__(self, size=(8, 8), pos=(0, 0)):
        super(Block, self).__init__()
        self.image = pygame.Surface(size)
        self.image.fill((randint(0, 255), randint(0, 255), randint(0, 255)))
        self.rect = self.image.get_rect().move(pos)


class Ball(pygame.sprite.Sprite):
    def __init__(self, size, pos=(0, 0)):
        super(Ball, self).__init__()
        self.image = pygame.Surface(size)
        pygame.draw.circle(self.image, WHITE, self.image.get_rect().center, int(size[0] / 2))
        self.rect = self.image.get_rect().move(pos)
        self.position = Vector2D(*pos)
        self.velocity = Vector2D(150, 150)

        self.bounce_sound = pygame.mixer.Sound("sounds/Bounce.wav")
        self.block_hit_sound = pygame.mixer.Sound("sounds/Block_hit.wav")

    def border_collision(self, screen):
        if self.rect.right > screen.right:
            self.velocity.x *= -1
            self.rect.right = screen.right
            self.position.x = self.rect.centerx
        elif self.rect.left < screen.left:
            self.velocity.x *= -1
            self.rect.left = screen.left
            self.position.x = self.rect.centerx
        elif self.rect.top < screen.top:
            self.velocity.y *= -1
            self.rect.top = screen.top
            self.position.y = self.rect.centery
        elif self.rect.top > screen.bottom:
            self.kill()
            pygame.event.post(pygame.event.Event(GAME_OVER_EVENT))
            return False
        else:
            return False
        return True

    def collision(self, sprite_collided, last, new):
        if not sprite_collided:
            return False
        elif len(sprite_collided) == 1 and sprite_collided[0] is self:
            return False

        for sprite in sprite_collided:
            if isinstance(sprite, Block):
                sprite.kill()

            sprite = sprite.rect
            if last.right <= sprite.left < new.right:
                # Hit from the right.
                self.velocity.x *= -1.05
                self.velocity.y *= 1.05
                self.rect.right = sprite.left
                self.position.x = self.rect.centerx
            elif last.left >= sprite.right > new.left:
                # Hit from the left.
                self.velocity.x *= -1.05
                self.velocity.y *= 1.05
                self.rect.left = sprite.right
                self.position.x = self.rect.centerx
            if last.bottom <= sprite.top < new.bottom:
                # Hit from above.
                self.velocity.y *= -1.05
                self.velocity.x *= 1.05
                self.rect.bottom = sprite.top
                self.position.y = self.rect.centery
            elif last.top >= sprite.bottom > new.top:
                # Hit from below.
                self.velocity.y *= -1.05
                self.velocity.x *= 1.05
                self.rect.top = sprite.bottom
                self.position.y = self.rect.centery

        return True

    def update(self, screen, seconds, game_objects, *ignored):
        last = self.rect.copy()
        self.position += self.velocity * seconds
        self.rect.center = self.position.x, self.position.y
        new = self.rect

        if self.collision(pygame.sprite.spritecollide(self, game_objects, dokill=False), last, new):
            self.block_hit_sound.play()
        if self.border_collision(screen):
            self.bounce_sound.play()


class Game:

    def __init__(self, screen):
        self.screen = screen
        self.area = screen.get_rect()
        self.player = Paddle(size=(self.area.width / 10, self.area.height / 30),
                             pos=self.area.midbottom,
                             origin="midbottom")
        self.game_objects = pygame.sprite.Group()
        self.game_objects.add(self.player)
        self.create_game_objects()
        self.running = True
        self.starting = True
        self.game_over = False
        font = pygame.font.SysFont('Arial', 16)
        self.start_text     = font.render('Press SPACE to start!', True, WHITE)
        self.game_over_text = font.render('GAME OVER', True, WHITE)

    def create_game_objects(self):
        width = self.area.width / 10
        height = self.area.width / 30
        for y in range(5):
            for x in range(10):
                self.game_objects.add(Block(size=(width-2, height-2), pos=(x * width + 1, y * height + 1)))

    def handle_events(self):
        key = pygame.key.get_pressed()
        if key[pygame.K_RIGHT]:
            self.player.velocity_x = 250
        elif key[pygame.K_LEFT]:
            self.player.velocity_x = -250
        else:
            self.player.velocity_x = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.running = False
                if event.key == pygame.K_SPACE and self.starting:
                    self.starting = False
            elif event.type == GAME_OVER_EVENT:
                self.game_over = True

    def main(self):
        clock = pygame.time.Clock()
        fps = 60
        ball = Ball(size=(8, 8), pos=self.area.move(0, -32).center)
        self.game_objects.add(ball)
        while self.running:
            seconds = clock.tick(fps) / 1000.0
            self.handle_events()
            self.screen.fill(BLACK)
            if self.starting:
                rect = self.start_text.get_rect(center=self.screen.get_rect().center)
                self.screen.blit(self.start_text, rect)
            elif self.game_over:
                rect = self.game_over_text.get_rect(center=self.screen.get_rect().center)
                self.screen.blit(self.game_over_text, rect)
            else:
                self.game_objects.update(self.area, seconds, self.game_objects)
            self.game_objects.draw(self.screen)
            pygame.display.update()


if __name__ == '__main__':
    pygame.init()
    SCREEN = pygame.display.set_mode((720, 480))
    while True:
        game = Game(SCREEN)
        game.main()
























