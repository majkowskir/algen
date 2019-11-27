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

iteracja = 0 # wartość startowa, warunek dla iteracja = Gen

# Parametry początkowe programu: liczba pokoleń (Gen), liczba zmiennych w funkcji (k), przedział (Xmin, Xmax), dokładność (d)
Gen = 50

# pop_size - liczebność populacji, dobrze, aby była parzysta
pop_size = 150

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
d = 3

# obliczamy, ile wartości musimy zakodować binarnie: mi
mi = ((Xmax-Xmin)*10**d)+1

# ...oraz ile bitów potrzebujemy, aby zakodować tyle wartości: m
# używamy logarytmu o podstawie 2 oraz funkcji ceiling (zwraca najbliższą liczbę całkowitą - większą lub równą wskazanej)
# uwaga: badamy funkcję jednej zmiennej (k=1), program nie przewiduje wielu zmiennych!
m = math.ceil(math.log(mi,2)) 

print("Dla zadanej dokładności i przedziału niezbędne jest zakodowanie minimum %s wartości, użyjemy do tego %s bitów." % (mi, m))

def funkcja(argument):
    try:
        y = (math.exp(argument) * math.sin(10*math.pi*argument)+1)/argument
    except:
        print("UWAGA! Błąd obliczania wartości funkcji dla argumentu x = %s" % argument) 
        y = 0
    return(y)

class Osobnik:

	# obsadzamy pierwszą populację (pop_size) losowymi wartościami 0/1 wg wyliczonej liczby bitów; pomiędzy chromosoamami nie unikamy powtórzeń
	def __init__(self):
		v_chromosom = np.random.choice(a=[0, 1], size=m)
		self.chromosom = v_chromosom

	def mutacja(self):
		pozycja_mutacji = rand.randint(0, m-1)
		self.chromosom[pozycja_mutacji] = abs(self.chromosom[pozycja_mutacji]-1)
		return (self.chromosom, pozycja_mutacji)

	def kopiowanie(self):
		return self.chromosom

	def crossover(self, pula):
		punkt_krzyzowania = rand.randint(1, m-2) # punkt krzyżowania, przecięcie chromosomu najwcześniej za pierwszym bitem, najpóźniej za przedostatnim
		rodzic_2 = rand.randint(0, pop_size-1)
	
		parent_2 = pula.stado[rodzic_2].chromosom
		dziecko_1 = np.concatenate((self.chromosom[:punkt_krzyzowania], parent_2[punkt_krzyzowania:]), axis=None)   
		dziecko_2 = np.concatenate((parent_2[:punkt_krzyzowania], self.chromosom[punkt_krzyzowania:]), axis=None)
		self.chromosom = dziecko_1
		
		pula.stado[rodzic_2].chromosom = dziecko_2
		#return (self.chromosom, parent_2, punkt_krzyzowania, dziecko_1, dziecko_2) # lista dla dwóch zwracanych wartości
		return (dziecko_1, dziecko_2)
		

class Populacja:

	def __init__(self, liczebnosc_stada):
		self.stado = []
		for i in range(liczebnosc_stada):
			self.stado.append(Osobnik())

	def ewaluacja(self):
	    wartosci_f = [] # usunięcie danych z listy do przechowywania wartosci funkcji dla danego pokolenia
	    for i in range(pop_size):
	        my_lst = self.stado[i].chromosom
	        str1=""
	        str1 = "".join(map(str, my_lst)) # łączenie elementów listy w string
	        dekodowanie2dec = int(str1, 2) # dekodowanie binarki do liczby dziesiętnej 
	        argument = ((Xmax-Xmin)*dekodowanie2dec)/((2**m)-1)+Xmin # mapowanie chromosomu do wartości x z zakresu (Xmin,Xmax)

	        wartosc = funkcja(argument) # wartość funkcji w punkcie x 
	        if wartosc < 0: wartosc = 0 # zapewniamy dla ruletki wartości dodatnie przez wyzerowanie ujemnych

	        #wartosci_f.append([round(argument,d), round(wartosc,d)])
	        wartosci_f.append([argument, wartosc])
	    return(wartosci_f)
	
	def ruletka(self):
		ewal =  self.ewaluacja()
		F = [sum(i) for i in zip(*ewal)] # https://www.geeksforgeeks.org/python-position-summation-in-list-of-tuples/
		F = F[1] # suma wszystkich wartości funkcji w stadzie

		Ps=[] # prawdopodobieństwa poszczególnych osobników, im większa wartość tym "więcej miejsca na kole"
		try:
			for x in ewal:
				Ps.append(x[1]/F)
		except:
			print("Suma prawdopodobieństw wynosi zero!")

		sektor = 0
		kolo_ruletki = []
		for i in range(pop_size):
			sektor = sektor + Ps[i]
			kolo_ruletki.append(sektor) # dodawanie do listy wartości brzegowej sektora

		pula_rodzicielska = []
		for i in range(pop_size): 
			losowa = rand.random() # losujemy liczbę z przedziału (0,1) tyle razy, ile osobników w populacji
			sektor = 0 # zaczynamy od sektora zero
			for j in range(len(kolo_ruletki)): # sprawdzamy, do którego sektora na kole ruletki wpadła wylosowana liczba
				if losowa > kolo_ruletki[j]:
					sektor=sektor+1
			pula_rodzicielska.append(self.stado[sektor].chromosom) # do puli rodzicielskiej dodajemy osobnika z puli zero
		
		# nadpisanie stada pulą rodzicielską
		for i in (range(len(pula_rodzicielska))):
			self.stado[i].chromosom = pula_rodzicielska[i]
		return()

	def operacje(self, pula):
		for i in range(pop_size):
			operacja = rand.random()
			if operacja > (Pc+Pm):
				self.stado[i].kopiowanie()
			elif operacja > Pm:
				self.stado[i].crossover(pula)
			else:
				self.stado[i].mutacja()
		return("ok")

Stado_Alfa = Populacja(pop_size) # utworzenie stada A

# wypisanie osobników w stadzie A
for i in range(pop_size):
	print(Stado_Alfa.stado[i].chromosom)

for iteracja in range(Gen):
	Stado_Alfa.ewaluacja()
	Stado_Alfa.ruletka()
	Stado_Alfa.operacje(Stado_Alfa)


print("Po x iteracjach")
for i in range(pop_size):
	print(Stado_Alfa.stado[i].chromosom)

print(*Stado_Alfa.ewaluacja(), sep="\n")
