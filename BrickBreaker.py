#!/usr/bin/env python3
import pygame as pg
import random

#Overlay object is a positionable sprite that will print whatever text
#you feed it through setText. Used by the game object to display score
#and lives while the game is running, or the win/lose condition
class Overlay(pg.sprite.Sprite):
    def __init__(self, screen, text='text', pos=(0,0), font=None, size=20, color=(0,0,0), antialias=True):
        super().__init__()
        self.font = pg.font.SysFont(font, size)
        self.color = color
        self.__text = text
        self.screen = screen
        self.antialias = antialias
        self.pos = pos
        self.__rerender()
        
    def setText(self, text): #sets self.text
        self.__text = text
        self.__rerender()
        
    def __rerender(self): #renders self.text at specified position
        self.image = self.font.render(self.__text, self.antialias, self.color)
        self.rect = self.image.get_rect()
        self.rect.x = self.pos[0]
        self.rect.y = self.pos[1]

#Paddle object is a user movable sprite that interacts with the ball objects
#in game.
class Paddle(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pg.Surface((250, 20))
        self.rect = self.image.get_rect()
        self.rect.x = 400
        self.rect.y = 550
        self.image.fill((0,0,0))
        self.__speed = 15
        
    def update(self): #Move paddle in a linear motion along the bottom of the screen with arrow keys
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.__speed
        if keys[pg.K_RIGHT] and self.rect.right < 800:
            self.rect.x += self.__speed

#Block object is a stationary collidable sprite that is destroyable in game.
#It regulates its death condition and deletes itself when out of hp.
class Block(pg.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        r = random.randint
        self.image = pg.Surface((100, 40))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.r = r(0, 255)
        self.g = r(0, 255)
        self.b = r(0, 255)
        self.image.fill((self.r,self.g,self.b))
        self.__hp = self.__life()
    
    def __life(self): #determines how much hp the block should have based on its color
        return 766 - self.r - self.g - self.b
        
    def hit(self): #Called when a ball collides with block, handles hp and color change based on losing hp
        self.__hp -= 24 #24 per hit instead of 25 as per directions because 24/3 = 8
        if self.__hp <= 0:
            self.kill() #Also deletes itself when no more hp

        if self.r <= 246:
            self.r += 8
        if self.g <= 246:
            self.g += 8
        if self.b <= 246:
            self.b += 8
        self.image.fill((self.r, self.g, self.b))
        
#Ball object is a sprite that bounces upon collision with other objects, and handles many
#of its collisions in the update function. Its velocity exponentially speeds up on bounce but
#the velocity is capped at 12 pixels per frame. Does damage to blocks and plays sound
class Ball(pg.sprite.Sprite):
    blocks = None
    def __init__(self):
        super().__init__()
        self.__SIZE = 23
        self.image = pg.Surface((self.__SIZE,self.__SIZE))
        self.image.fill((255, 255, 255))
        pg.draw.circle(self.image, (0, 101, 164), (self.__SIZE/2, self.__SIZE/2), self.__SIZE/2)
        self.rect = self.image.get_rect()
        self.rect.x = 400
        self.rect.y = 400
        self.__velocity = [3,-3]
        self.blocks = None
        self.paddle = None
        self.boom = pg.mixer.Sound(file = "Boom.wav")

    #update ball each frame, fed game as a parameter so that it can call functions to change game variables
    def update(self, game):
        #Move ball this frame by velocity
        self.rect.x += self.__velocity[0]
        self.rect.y += self.__velocity[1]
        #Handle bouncing off walls
        if self.rect.x < 0:
            self.rect.x -= 1*self.__velocity[0]-1
            self.rect.y -= 1*self.__velocity[1]-1
            self.__velocity[0] = -self.__velocity[0]
        if self.rect.x > 800 - self.__SIZE:
            self.rect.x -= 1*self.__velocity[0]-1
            self.rect.y -= 1*self.__velocity[1]-1
            self.__velocity[0] = -self.__velocity[0]
        if self.rect.y < 0:
            self.rect.x -= 1*self.__velocity[0]-1
            self.rect.y -= 1*self.__velocity[1]-1
            self.__velocity[1] = -self.__velocity[1]

        #If ball hits bottom of screen, take a life from game and remove ball
        if self.rect.y > 600 - self.__SIZE:
            self.kill()
            game.takeLife()
        
        for paddle in Ball.paddle: #Handle paddle collison
            if pg.Rect.colliderect(self.rect, paddle): #using built in collision detection
                self.rect.x -= (1*self.__velocity[1]+1)
                self.__velocity[1] *= -1.03
                self.__velocity[0] *= 1.03

        for block in Ball.blocks: #Handle block collision
            #if ball collides with block
            if pg.Rect.colliderect(self.rect, block): #using built in collision detection
                #handle colliding with top/bottom or a side
                if self.rect.right > block.rect.x  and self.rect.left < block.rect.x + 100:
                    self.rect.x -= (1*self.__velocity[0]-1)
                    self.rect.y -= (1*self.__velocity[1]-1)
                    self.__velocity[1] *= -1.03
                    self.__velocity[0] *= 1.03  
                elif self.rect.centery > ((block.rect.top - self.__SIZE/2)+1) and self.rect.centery < ((block.rect.bottom + self.__SIZE/2)-1):
                    self.rect.x -= (1*self.__velocity[0]-1)
                    self.rect.y -= (1*self.__velocity[1]-1)
                    self.__velocity[0] *= -1.03
                    self.__velocity[1] *= 1.03
                else: #handles edge cases by at least doing something to keep ball in bounds if collision code fails
                    self.rect.x -= (1*self.__velocity[0]-1)
                    self.rect.y -= (1*self.__velocity[1]-1)
                    self.__velocity[1] *= -1.03
                    self.__velocity[0] *= -1.03
                self.__velocity[0] = min(12, self.__velocity[0]) #cap velocity at 12
                self.__velocity[1] = min(12, self.__velocity[1])
                self.boom.play()
                block.hit()
                game.addScore()
        
    def setBlocks(self, blocks):
        self.blocks = blocks

#Game object manages the other objects and holds game data, 
#game updating, event handling, drawing objects, and win/lose handling
class Game:
    def __init__(self):
        pg.init()
        pg.mixer.music.load("background.wav")
        pg.mixer.music.play(-1, 0.0)
        self.__running = False
        self.__score = 0
        self.__lives = 10
        self.screen = pg.display.set_mode( (800, 600) )
        self.clock = pg.time.Clock()
        self.balls = pg.sprite.Group() #__ to mark private instance variables!
        self.blocks = pg.sprite.Group()
        self.paddle = pg.sprite.Group()
        self.sprites = pg.sprite.RenderUpdates()
        self.infoText = Overlay(self.screen, 'Score: '+ str(self.__score) + '   Lives: ' + str(self.__lives),
            (0,570), "Arial", 24, (0,0,0), True)
        self.sprites.add(self.infoText)

    def run(self): #Game loop. represents each frame that happens
        while self.__running:
            # Take events
            events = pg.event.get()
            for event in events:
                if event.type == pg.QUIT:
                    self.__running = False
                    pg.quit()
                    exit()
                if event.type == pg.KEYDOWN:
                    key = pg.key.get_pressed()
                    if key[pg.K_1]:             #press key "1" to spawn new/extra ball
                        self.addBall(Ball())
            
            # Update updateable objects
            self.paddle.update()
            self.balls.update(self) 

            blocks = 0
            for block in self.blocks: #count how many blocks are left in the game
                blocks += 1

            if blocks <= 0: #Win/lose conditions else keep displaying lives and score
                for ball in self.balls:
                    ball.kill()
                self.infoText.setText("You Win! Score: " + str(self.__score))
            elif self.__lives <= 0:
                for ball in self.balls:
                    ball.kill()
                self.infoText.setText('GAME OVER, EXIT AND RELAUNCH TO RESTART')
            else:
                self.infoText.setText(
                    'Score: ' + str(self.__score) + '   Lives: ' + str(self.__lives))
                
            # Redraw
            self.screen.fill( (255, 255, 255) )
            self.balls.draw(self.screen)
            self.blocks.draw(self.screen)
            self.paddle.draw(self.screen)
            self.sprites.draw(self.screen)
            pg.display.flip()
            self.clock.tick(60)
        
    def addScore(self):
        self.__score += 25
    
    def takeLife(self):
        self.__lives -= 1

    def setRunning(self, running):
        self.__running = running

    def addBall(self, ball):
        self.balls.add(ball)
    
    def addPaddle(self, paddle):
        self.paddle.add(paddle)

    def addBlock(self, block):
        self.blocks.add(block)

    def getBlocks(self):
        return self.blocks
    
    def getPaddle(self):
        return self.paddle

def main():
    game = Game()
    game.addBall( Ball() )
    game.addPaddle(Paddle())

    for i in range(0,8): #create a grid of game blocks filling the top of the screen
        for j in range(0,5):
            game.addBlock(Block(i*100, j*40))

    Ball.blocks = game.getBlocks()
    Ball.paddle = game.getPaddle()
    game.setRunning(True)
    game.run()

if __name__ == '__main__':
    main()
