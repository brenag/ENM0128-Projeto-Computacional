    # -*- coding: utf-8 -*-
#Solucção Numérica da Equação Geral da Condução de Calor utilizando o Método das Diferenças Finitas
#Aluno: Emanuel Couto Brenag
#ENM0128 - Transporte de Calor e Massa


import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
import math
import time

#setar dimensão e delta
lenX = lenY = 90 #setamos a malha como retangular
delta = 1
#estes não são os valores reais do delta e do comprimento. O tamanho da malha é constante, lenX é o número de nós por linha e coluna e o valor real de delta é definido por 3 / lenX
#Alguns truques que usei para preencher as lacunas dentro da matriz e definir o buraco 1x1 no centro
knots = lenX/delta 

hole_x  = math.floor(knots/3)
hole_y  = math.floor(knots/3)

hole_x_range = round(knots/3)
hole_y_range = round(knots/3)

#Define a condutividade térmica de um material específico

k= 80
#Define a difusividade térmica de um material específico
alpha= 0.25

#Define a constante de geração interna
H= 10
int_gen= H*(3/lenX)**2/k 

#Define o intervalo temporal para o número de Fourier (delta_t)

delta_t=1
#Define o número de Fourier
factor = alpha*delta_t/(delta**2)



#Condição de contorno para a mashgrid

Ttop = 100
Tbottom = 100
Tleft = 100
Tright = 300

#Condição inicial da parte interna da malha definida como 0
Tguess = 0

#Seta a interpolação de cor e colour map
colorinterpolation = 50
colourMap = plt.cm.jet #you can try: colourMap = plt.cm.coolwarm   

# Set meshgrid
X, Y = np.meshgrid(np.linspace(0, 3, lenX), np.linspace(0, 3, lenY))

#Seta o tamanho do array e a temperatura interna com Tguess

T = np.empty((lenX, lenY))
T.fill(Tguess)

#Seta as condições de contorno

#Precisamos setar as condições de contorno de modo a manter os nós internos nulos (a parte do furo)

T[(lenY-1):, :] = Ttop
T[:1, :] = Tbottom
T[:, (lenX-1):] = Tright
T[:, :1] = Tleft

#Seta as condições de contorno nas paredes do furo
T[hole_y, hole_x :(hole_x + hole_x_range)] = 20 
T[hole_y + hole_y_range , hole_x: (hole_x + hole_x_range)] = 15 
T[hole_y : (hole_y + hole_y_range + 1), hole_x] = 10 
T[hole_y : (hole_y + hole_y_range + 1), (hole_x + hole_x_range)] = 30 
T[hole_y + 1 : (hole_y + hole_y_range), hole_x + 1 : (hole_x + hole_x_range)] = 0

#classe que define as iterações e evita qeu a matriz em t=t+1 itere com t=t

class Grid:
  def __init__(self, matrix, Ttop, Tbottom, Tleft, Tright, factor, int_gen):
    self.state = [[]]
    self.state[0] = matrix
    self.top = Ttop
    self.bottom = Tbottom
    self.left = Tleft
    self.right = Tright
    self.factor = factor
    self.int_gen = int_gen
  def iterate(self, iterations):
    for i in range(iterations):
      aux = self.state[len(self.state)-1]
      aux2 = np.zeros((len(aux), len(aux[0])))
      for i in range(1, len(aux)-1, delta):
          for j in range(1, len(aux[0])-1, delta):
              aux2[i][j] = self.factor*(aux[i+1][j] + aux[i-1][j] + aux[i][j+1] + aux[i][j-1]) + (1-4*self.factor)*(aux[i][j]) + self.int_gen

#apenas para ter a certeza de as condições de contorno se mantém constantes
      aux2[(lenY-1):, :] = self.top
      aux2[:1, :] = self.bottom
      aux2[:, (lenX-1):] = self.right
      aux2[:, :1] = self.left

      aux2[hole_y, hole_x :(hole_x + hole_x_range)] = 20 
      aux2[hole_y + hole_y_range , hole_x: (hole_x + hole_x_range)] = 15 
      aux2[hole_y : (hole_y + hole_y_range + 1), hole_x] = 10 
      aux2[hole_y : (hole_y + hole_y_range + 1), (hole_x + hole_x_range)] = 30 
      aux2[hole_y + 1 : (hole_y + hole_y_range), hole_x + 1 : (hole_x + hole_x_range)] = 0 
      self.state.append(aux2)

  def getState(self, t):
    return self.state[t]

#essa função define condições para a animação
def animate(t, grid):
  cont = ax.contourf(X, Y, grid.getState(t*5), colorinterpolation, cmap=colourMap)

#essa parte do código recebe T, Fourier e a geração interna com o intuito de calcular o tempo computacional gasto para fazer as iterações

test_cases = [(T, factor, int_gen)]
times = []
grids = []
for test in test_cases:
  start = time.time()
  grid = Grid(test[0], Ttop, Tbottom, Tleft, Tright, test[1], test[2])
  grid.iterate(5000)
  grids.append(grid)
  times.append(time.time()- start)

grids[0].getState(5000)

print(times)

#essa parte do código cria um arquivo .mp4 com os plots desde o tempo inicial até o tempo escolhido
#leva um bom tempo, então comente esse trecho do código caso só queira os perfis nos tempos finais
frames = 5000
grid = Grid(T, Ttop, Tbottom, Tleft, Tright, 0.25, 0.125)
grid.iterate(frames)

fig = plt.figure()
ax = plt.axes(xlim=(0, 3), ylim=(0, 3))  
plt.xlabel(r'x')
plt.ylabel(r'y')
cont = ax.contourf(X, Y, grid.getState(0), colorinterpolation, cmap=colourMap)
cb = fig.colorbar(cont)
anim = animation.FuncAnimation(fig, animate, fargs=(grid,), frames=frames//5, save_count=frames//5)
writermp4 = animation.FFMpegFileWriter(fps=50, bitrate=1800)
anim.save('animação.mp4', writer=writermp4)

# plt.show()
#plota o perfil final

fig = plt.figure()
ax = plt.axes(xlim=(0, 3), ylim=(0, 3))  
plt.xlabel(r'x')
plt.ylabel(r'y')
contourplot = plt.contourf(X, Y, grid.getState(5000), colorinterpolation, cmap=colourMap)
cbar = plt.colorbar(contourplot)
plt.show()

#a partir daqui são plotados os perfis de temperatura em diferentes partes da malha
def column(matrix, i):
  return [row[i] for row in matrix]

Temperatura= column(grid.getState(3000),15)
plt.plot(np.linspace(0,3,len(Temperatura)),Temperatura)
plt.title('Perfil de temperatura do eixo y no comprimento x=0,5m')
plt.xlabel('Posição no eixo y')
plt.ylabel('Temperatura (K)')
plt.show()

Temperatura= column(grid.getState(3000),45)
plt.plot(np.linspace(0,3,len(Temperatura)),Temperatura)
plt.title('Perfil de temperatura do eixo y no comprimento x=1,5m')
plt.xlabel('Posição no eixo y')
plt.ylabel('Temperatura (K)')
plt.show()

Temperatura= grid.getState(3000)[45][:]
plt.plot(np.linspace(0,3,len(Temperatura)),Temperatura)
plt.title('Perfil de temperatura do eixo x na altura y=1,5m')
plt.xlabel('Posição no eixo x')
plt.ylabel('Temperatura (K)')
plt.show()

Temperatura= grid.getState(3000)[89][:]
plt.plot(np.linspace(0,3,len(Temperatura)),Temperatura)
plt.title('Perfil de temperatura do eixo x na altura y=3,0m')
plt.xlabel('Posição no eixo x')
plt.ylabel('Temperatura (K)')
plt.show()

Temperatura= grid.getState(3000)[15][:]
plt.plot(np.linspace(0,3,len(Temperatura)),Temperatura)
plt.title('Perfil de temperatura do eixo x na altura y=0,5m')
plt.xlabel('Posição no eixo x')
plt.ylabel('Temperatura (K)')
plt.show()