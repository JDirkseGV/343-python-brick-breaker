#!/usr/bin/env python3

from cgitb import text
import os
from turtle import color, screensize
import pygame as pg
import random

class Overlay(pg.sprite.Sprite):
    def __init__(self, screen, text='text', pos=(0,0), font=None, size=20, color=(0,0,0), antialias=True):
        super().__init__()
        self.font = pg.font.SysFont(font, size)
        self.color = color
        self.text = text
        self.screen = screen
        self.antialias = antialias
        self.pos = pos
        self.rerender()
        
    
    def printText(self, text):
        self.text = text
        self.rerender()
        
    def rerender(self):
        self.image = self.font.render(self.text, self.antialias, self.color)
        self.rect = self.image.get_rect()
        self.rect.x = self.pos[0]
        self.rect.y = self.pos[1]

        

        

    
    
    
        

class Paddle(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pg.Surface((250, 20))
        self.rect = self.image.get_rect()
        self.rect.x = 400
        self.rect.y = 550
        self.image.fill((0,0,0))
        self.speed = 15
        
    def update(self):
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pg.K_RIGHT] and self.rect.right < 800:
            self.rect.x += self.speed



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
        self.hp = self.life()
    
    def life(self):
        return 766 - self.r - self.g - self.b
        

    def hit(self):
        self.hp -= 24
        
        if self.hp <= 0:
            self.kill()
        if self.r <= 246:
            self.r += 8
        if self.g <= 246:
            self.g += 8
        if self.b <= 246:
            self.b += 8
        self.image.fill((self.r, self.g, self.b))
        

class Ball(pg.sprite.Sprite):
    blocks = None
    def __init__(self):
        super().__init__()

        self.SIZE = 23
        
        
        self.image = pg.Surface((self.SIZE,self.SIZE))
        self.image.fill((255, 255, 255))
        pg.draw.circle(self.image, (0, 101, 164), (self.SIZE/2, self.SIZE/2), self.SIZE/2)
        self.rect = self.image.get_rect()
        self.rect.x = 400
        self.rect.y = 400
        self.velocity = [3,-3]
        self.blocks = None
        self.paddle = None
        self.boom = pg.mixer.Sound(file = "Boom.wav")

    def update(self, game):
           
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        if self.rect.x < 0:
            self.rect.x -= 1*self.velocity[0]-1
            self.rect.y -= 1*self.velocity[1]-1
            self.velocity[0] = -self.velocity[0]
        if self.rect.x > 800 - self.SIZE:
            self.rect.x -= 1*self.velocity[0]-1
            self.rect.y -= 1*self.velocity[1]-1
            self.velocity[0] = -self.velocity[0]
        if self.rect.y < 0:
            self.rect.x -= 1*self.velocity[0]-1
            self.rect.y -= 1*self.velocity[1]-1
            self.velocity[1] = -self.velocity[1]
        if self.rect.y > 600 - self.SIZE:
            self.kill()
            game.takeLife()
            #self.rect.x -= 1*self.velocity[0]-1
            #self.rect.y -= 1*self.velocity[1]-1
            #self.velocity[1] = -self.velocity[1]

        for paddle in Ball.paddle:
            if self.rect.top < paddle.rect.bottom and self.rect.right > paddle.rect.left and self.rect.left < paddle.rect.right and self.rect.bottom > paddle.rect.top:
                self.rect.x -= (1*self.velocity[0]+1)
                self.rect.y -= (1*self.velocity[1]+1)
                self.velocity[1] *= -1.03
                self.velocity[0] *= 1.03

        for block in Ball.blocks:
            if self.rect.top < block.rect.bottom and self.rect.right > block.rect.left and self.rect.left < block.rect.right and self.rect.bottom > block.rect.top:
                
                if self.rect.right > block.rect.x  and self.rect.left < block.rect.x + 100:
                    self.rect.x -= (1*self.velocity[0]-1)
                    self.rect.y -= (1*self.velocity[1]-1)
                    self.velocity[1] *= -1.03
                    self.velocity[0] *= 1.03
                        
                elif self.rect.centery > ((block.rect.top - self.SIZE/2)+1) and self.rect.centery < ((block.rect.bottom + self.SIZE/2)-1):
                    self.rect.x -= (1*self.velocity[0]-1)
                    self.rect.y -= (1*self.velocity[1]-1)
                    self.velocity[0] *= -1.03
                    self.velocity[1] *= 1.03
                else:
                    self.rect.x -= (1*self.velocity[0]-1)
                    self.rect.y -= (1*self.velocity[1]-1)
                    self.velocity[1] *= -1.03
                    self.velocity[0] *= -1.03
                self.velocity[0] = min(12, self.velocity[0])
                self.velocity[1] = min(12, self.velocity[1])
                self.boom.play()
                block.hit()
                game.addScore()
        
            

    def setBlocks(self, blocks):
        self.blocks = blocks

class Game:
    def __init__(self):
        pg.init()
        
        self.__running = False
        self.score = 0
        self.lives = 5
        self.screen = pg.display.set_mode( (800, 600) )
        self.clock = pg.time.Clock()
        self.balls = pg.sprite.Group() #__ to mark private instance variables!
        self.blocks = pg.sprite.Group()
        self.paddle = pg.sprite.Group()
        self.sprites = pg.sprite.RenderUpdates()
        self.info_text = Overlay(self.screen, 'Score: '+ str(self.score) + '   Lives: ' + str(self.lives),
            (0,570), "Arial", 24, (0,0,0), True)
        self.sprites.add(self.info_text)

    def run(self):
        while self.__running:
            events = pg.event.get()
            for event in events:
                if event.type == pg.QUIT:
                    self.__running = False
                    pg.quit()
                    exit()
            # Take events

            # Update updateable objects
            key = pg.key.get_pressed()
            
            if key[pg.K_1]:
                self.addBall(Ball())
            self.paddle.update()
            self.balls.update(self)
            
            self.info_text.printText(
                'Score: ' + str(self.score) + '   Lives: ' + str(self.lives))    
            
            

            # Redraw
            self.screen.fill( (255, 255, 255) )
            self.balls.draw(self.screen)
            self.blocks.draw(self.screen)
            self.paddle.draw(self.screen)
            self.sprites.draw(self.screen)
            pg.display.update()
            
            
            
            
            

            
            pg.display.flip()
            self.clock.tick(60)
        
    def addScore(self):
        self.score += 25
    
    def takeLife(self):
        self.lives -= 1

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
    for i in range(0,8):
        for j in range(0,5):
            game.addBlock(Block(i*100, j*40))
    Ball.blocks = game.getBlocks()
    Ball.paddle = game.getPaddle()
    game.setRunning(True)
    game.run()

if __name__ == '__main__':
    main()
