# Wyznaczanie maksimum funkcji algorytmem ewolucyjnym
# Radosław Majkowski 233256 
# Mateusz Witomski 233270

import time, math, matplotlib
import matplotlib.pyplot as plt
import numpy as np
import random as rand

from collections import Counter

import tkinter as tk
from tkinter import *



# funckja przystosowania, wpisana zgodnie z warunkami zadania laboratoryjnego
# uwaga 1: dziedzina funkcji wyklucza zero
# uwaga 2: reguła ruletki nie dopuszcza ujemnych wartości funkcji celu; znamy orientacyjne wartości w interesującyjm przedziale,
# dlatego "podnosimy" wartość o bezpieczne 7

shift = 7 # przesunięcie wartości funkcji w osi Y
iteracja = 0 # wartość startowa, warunek dla iteracja = Gen

shift = 7 # przesunięcie wartości funkcji w osi Y
iteracja = 0 # wartość startowa, warunek dla iteracja = Gen

def funkcja(argument):
    try:
        y = (math.exp(argument) * math.sin(10*math.pi*argument)+1)/argument
        # y = math.sin(argument) # testowa funkcja kontrolna, w testowym zakresie max=1
    except:
        print("UWAGA! Błąd obliczania wartości funkcji dla argumentu x = %s" % argument) 
        y = 0
    return(y+shift)

# Parametry początkowe programu: liczba pokoleń (Gen), liczba zmiennych w funkcji (k), przedział (Xmin, Xmax), dokładność (d)
Gen = 25

# pop_size - liczebność populacji, dobrze, aby była parzysta
pop_size = 3

# prawdopodobieństwa: krzyżowania (Pc) oraz mutacji (Pm)
Pc = 0.75
Pm = 0.1

# Funkcja celu jest funkcją jednej zmiennej (k), nie jest używana w tej wersji programu
k = 1

# przedział w którym badamy funkcję (Xmin do Xmax)
# uwaga: w zadaniu występują tylko wartości dodatnie, nie ma potrzeby przesuwania przedziału
Xmin = 0.5
Xmax = 2.5

# dokładność: 3 miejsca po kropce dziesiętnej
d = 2

# obliczamy, ile wartości musimy zakodować binarnie: mi
mi = ((Xmax-Xmin)*10**d)+1

# ...oraz ile bitów potrzebujemy, aby zakodować tyle wartości: m
# używamy logarytmu o podstawie 2 oraz funkcji ceiling (zwraca najbliższą liczbę całkowitą - większą lub równą wskazanej)
# uwaga: badamy funkcję jednej zmiennej (k=1), program nie przewiduje wielu zmiennych!
m = math.ceil(math.log(mi,2)) 

print("Dla zadanej dokładności i przedziału niezbędne jest zakodowanie minimum %s wartości, użyjemy do tego %s bitów." % (mi, m))


# obsadzamy pierwszą populację (pop_size) losowymi wartościami 0/1 wg wyliczonej liczby bitów; pomiędzy chromosoamami nie unikamy powtórzeń
def f_Pokolenie_zero(f_pop_size, f_m, output=False):
    pokolenie_zero = np.random.choice(a=[0, 1], size=(f_pop_size, f_m)) # macierz o rozmiarach: populacja x bitowość, losowo 0/1
    if output: print(*pokolenie_zero, sep = "\n")
    print("Wygenerowano losową populację %s osobników, długość chromosomu: %s." % (f_pop_size, f_m))
    return(pokolenie_zero)

class Osobnik:

	def __init__(self):
		v_chromosom = np.random.choice(a=[0, 1], size=m)
		self.chromosom = v_chromosom

	def mutacja(self):
		pozycja_mutacji = rand.randint(0, m-1)
		self.chromosom[pozycja_mutacji] = abs(self.chromosom[pozycja_mutacji]-1)
		return (self.chromosom, pozycja_mutacji)

	def kopiowanie(self):
		return self.chromosom

	def crossover(self):
		punkt_krzyzowania = rand.randint(1, m-2) # punkt krzyżowania, przecięcie chromosomu najwcześniej za pierwszym bitem, najpóźniej za przedostatnim
		partnerka = rand.randint(0, pop_size-1)
		parent_2 = Populacja[partnerka].chromosom
		dziecko_1 = np.concatenate((self.chromosom[:punkt_krzyzowania], parent_2[punkt_krzyzowania:]), axis=None)   
		dziecko_2 = np.concatenate((parent_2[:punkt_krzyzowania], self.chromosom[punkt_krzyzowania:]), axis=None)

		self.chromosom = dziecko_1
		Populacja[partnerka].chromosom = dziecko_2
		#return (self.chromosom, parent_2, punkt_krzyzowania, dziecko_1, dziecko_2) # lista dla dwóch zwracanych wartości
		return (dziecko_1, dziecko_2)

class Populacja:

	def __init__(self):
		

Populacja=[]

for i in range(pop_size):
    Populacja.append(Osobnik())

print("Pokolenie zero: \n")
for obj in Populacja:
	print(obj.chromosom)


Populacja[0].mutacja()
print("Po mutacji \n")
for obj in Populacja:
	print(obj.chromosom)

Populacja[0].crossover()
print("Po krzyzowaniu \n")
for obj in Populacja:
	print(obj.chromosom)

