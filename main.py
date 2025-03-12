import pygame, sys, random
from pygame.locals import *

pygame.init()

rojo = (255, 0, 0)
blanco = (255, 255, 255)
negro = (0, 0, 0)

ANCHO, ALTO = 800, 600
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Galaga")

try:
    Nave_img = pygame.image.load("imagenes/Nave.png")
    Enemigo1_img = pygame.image.load("imagenes/Enemigo1.png")
    Enemigo2_img = pygame.image.load("imagenes/Enemigo2.png")
    Bala_img = pygame.image.load("imagenes/Bala.png")
    fondo = pygame.image.load("imagenes/fondo.png")
    planeta = pygame.image.load("imagenes/planeta.png")
except pygame.error as e:
    print(f"Error cargando la imagen: {e}")
    pygame.quit()
    sys.exit()

Nave_img = pygame.transform.scale(Nave_img, (100, 100))
Enemigo1_img = pygame.transform.scale(Enemigo1_img, (80, 80))
Enemigo2_img = pygame.transform.scale(Enemigo2_img, (80, 80))
Bala_img = pygame.transform.scale(Bala_img, (20, 30))
fondo = pygame.transform.scale(fondo, (800, 600))
planeta = pygame.transform.scale(planeta, (800, 600))

fuente = pygame.font.Font(None, 36)

y = 0
nave_x = ANCHO // 2 - Nave_img.get_width() // 2
nave_y = ALTO - Nave_img.get_height() - 10
velocidad_nave = 15
puntaje = 0
generacion_ultimo_enemigo = pygame.time.get_ticks()
intervalo_generacion = 500
tiempo_game_over = 0
duracion_game_over = 2000

sprites = pygame.sprite.Group()
enemigos = pygame.sprite.Group()
balas = pygame.sprite.Group()

def actualizar_fondo():
    global y
    y_relativa = y % fondo.get_rect().height
    pantalla.blit(fondo, (0, y_relativa - fondo.get_rect().height))
    if y_relativa < ALTO:
        pantalla.blit(fondo, (0, y_relativa))
    y += 1  

class Nave(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = Nave_img
        self.rect = self.image.get_rect()
        self.rect.center = (nave_x, nave_y)
        self.velocidad = velocidad_nave
        self.disparando = False

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and self.rect.left > 0:
            self.rect.x -= self.velocidad
        if keys[pygame.K_d or K_RIGHT] and self.rect.right < ANCHO:
            self.rect.x += self.velocidad

        if keys[pygame.K_SPACE] and not self.disparando:
            self.disparar()
            self.disparando = True
        if not keys[pygame.K_SPACE]:
            self.disparando = False

    def disparar(self):
        bala = Bala(self.rect.centerx, self.rect.top)
        balas.add(bala)
        sprites.add(bala)

class Bala(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = Bala_img
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.top = y
        self.velocidad = 10

    def update(self):
        self.rect.y -= self.velocidad
        if self.rect.bottom < 0:
            self.kill()

class Enemigo(pygame.sprite.Sprite):
    def __init__(self, x, y, imagen):
        super().__init__()
        self.image = imagen
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.velocidad = 6

    def update(self):
        self.rect.y += self.velocidad
        if self.rect.top > ALTO:
            self.kill()

explosion_frames = []
for i in range(1, 16):
    frame = pygame.image.load(f'animaciones/explosion_frame_corrected_{i}.png').convert_alpha()
    frame = pygame.transform.scale(frame, (100, 100))
    explosion_frames.append(frame)

class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.frames = explosion_frames
        self.index = 0
        self.image = self.frames[self.index]
        self.rect = self.image.get_rect(center=(x, y))
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 100 

    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_update > self.frame_rate:
            self.last_update = current_time
            self.index += 1
            if self.index < len(self.frames):
                self.image = self.frames[self.index]
            else:
                self.kill()  

def generar_enemigos():
    global generacion_ultimo_enemigo
    tiempo_actual = pygame.time.get_ticks()
    if tiempo_actual - generacion_ultimo_enemigo >= intervalo_generacion:
        generacion_ultimo_enemigo = tiempo_actual
        enemigo_img = random.choice([Enemigo1_img, Enemigo2_img])
        x_enemigo = random.randint(0, ANCHO - enemigo_img.get_width())
        y_enemigo = 0
        enemigo = Enemigo(x_enemigo, y_enemigo, enemigo_img)
        enemigos.add(enemigo)
        sprites.add(enemigo)

def revisar_colisiones():
    global puntaje
    colisiones = pygame.sprite.groupcollide(enemigos, balas, True, True)
    for enemigo in colisiones:
        puntaje += 1
        explosion = Explosion(enemigo.rect.centerx, enemigo.rect.centery)
        sprites.add(explosion)

def Game_Over():
    global jugando, tiempo_game_over
    for enemigo in enemigos:
        if pygame.sprite.collide_rect(enemigo, nave):
            enemigos.remove(enemigo)
            sprites.remove(enemigo)   
            nave.kill()

            jugando = False
            tiempo_game_over = pygame.time.get_ticks() 
            break

nave = Nave()
sprites.add(nave)

clock = pygame.time.Clock()
jugando = True

while True:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    sprites.update()
    generar_enemigos()
    revisar_colisiones()
    Game_Over()

    pantalla.fill(negro)
    pantalla.blit(fondo,(0,0))
    pantalla.blit(planeta,(0,0))

    if not jugando:
        tiempo_transcurrido = pygame.time.get_ticks() - tiempo_game_over
        if tiempo_transcurrido < duracion_game_over:
            texto_game_over = fuente.render("¡Game Over, Han invadido la tierra!", True, blanco)
            pantalla.blit(texto_game_over, (ANCHO // 2 - 200, ALTO // 2 - 50))
        else:
            pygame.quit()
            sys.exit()

    texto_puntaje = fuente.render(f"Puntaje: {puntaje}", True, blanco)
    pantalla.blit(texto_puntaje, (10, 10))

    sprites.draw(pantalla)

    pygame.display.flip()

    clock.tick(30)
