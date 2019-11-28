# Wyznaczanie maksimum funkcji algorytmem ewolucyjnym
# Radosław Majkowski 233256 
# Mateusz Witomski 233270

import time, math, matplotlib
import matplotlib.pyplot as plt

import numpy as np
import random as rand

#from collections import Counter

from operator import itemgetter

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
Pc = 0.25
Pm = 0.01

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
        #y = math.sin(argument)
    except:
        print("UWAGA! Błąd obliczania wartości funkcji dla argumentu x = %s" % argument) 
        y = 0
    return(y)

class Osobnik:

	# obsadzamy pierwszą populację (pop_size) losowymi wartościami 0/1 wg wyliczonej liczby bitów; pomiędzy chromosoamami nie unikamy powtórzeń
	def __init__(self):
		v_chromosom = np.random.choice(a=[0, 1], size=m)
		self.chromosom = v_chromosom

	def mutacja(self, rodzic_1):
		pass

	def kopiowanie(self):
		pass
		#return self.chromosom

	def crossover(self, rodzic_1, rodzic_2):
		punkt_krzyzowania = rand.randint(1, m-2) # punkt krzyżowania, przecięcie chromosomu najwcześniej za pierwszym bitem, najpóźniej za przedostatnim
		
		#print("Rodzic 1: %s" % rodzic_1)
		#print("Rodzic 2: %s" % rodzic_2)
		# print("Punkt krzyzowania: %s" % punkt_krzyzowania)

		try:
			dziecko_1 = np.concatenate((rodzic_1[:punkt_krzyzowania], rodzic_2[punkt_krzyzowania:]), axis=None)   
			dziecko_2 = np.concatenate((rodzic_2[:punkt_krzyzowania], rodzic_1[punkt_krzyzowania:]), axis=None)
		except:
			print("blad krzyzowania")
		# print("Dziecko 1: %s" % dziecko_1)
		# print("Dziecko 2: %s" % dziecko_2)
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
			print("sometink went wronk: np. suma prawdopodobieństw wynosi zero?!?")

		sektor = 0
		kolo_ruletki = []
		for i in range(len(Ps)):
			sektor = sektor + Ps[i]
			kolo_ruletki.append(sektor) # dodawanie do listy wartości brzegowej sektora

		losowa = rand.uniform(0,(kolo_ruletki[len(kolo_ruletki)-1])) # losujemy liczbę z przedziału (0, 1 lub czasami do 0,99999999 ) 
		sektor = 0 # zaczynamy od sektora zero
		for j in range(len(kolo_ruletki)): # sprawdzamy, do którego sektora na kole ruletki wpadła wylosowana liczba
			if losowa > kolo_ruletki[j]:
				sektor = sektor+1
		return(self.stado[sektor].chromosom)

	def operacje(self):
		potomstwo = []
		iteracja = iter(range(len(self.stado)))

		for i in iteracja:
			operacja = rand.random()
			if operacja > (Pc+Pm):
				try:
					potomstwo.append(self.ruletka())
				#	print(i, "\tIteracja operacyjna: kopiowanie")
				except:
					print("Błąd kopiowania!")
			elif operacja > Pm:
				rodzic_1 = self.ruletka()
				rodzic_2 = self.ruletka()
				dzieci = self.stado[i].crossover(rodzic_1, rodzic_2)
				try:
					next(iteracja)
					potomstwo.append(dzieci[0]) # tu jest brzydko, bo na twardo, powinna być jakaś pętla
					potomstwo.append(dzieci[1])
				except:
					potomstwo.append(dzieci[0]) # jeśli krzyzujemy ostatniego osobnika w puli, propagowane jest tylko jedno dziecko
				#print(i, "\tIteracja operacyjna: krzyżowanie")
			else:
				#print("mutowanie \n")
				pozycja_mutacji = rand.randint(0, m-1)
				rodzic_1 = self.ruletka()
				#print("Rodzic 1:", rodzic_1)
				#print("Pozycja mutacji: ", pozycja_mutacji)
				rodzic_1[pozycja_mutacji]=abs(rodzic_1[pozycja_mutacji]-1)
				mutant = rodzic_1
				potomstwo.append(mutant)
				#print(i, "\tIteracja operacyjna: mutacja")


		# przepisanie stada rodzicielskiego na potomne:
		for i in (range(len(potomstwo))): 
			#print(i,self.stado[i].chromosom," ",potomstwo[i])
			potomek = potomstwo[i]
			self.stado[i].chromosom = potomek
		return(potomstwo)

Stado_Alfa = Populacja(pop_size) # utworzenie stada A

# wypisanie osobników w stadzie A
# for i in range(pop_size):
# 	print(Stado_Alfa.stado[i].chromosom)

for iteracja in range(Gen):
	Stado_Alfa.operacje()
	wartosci = Stado_Alfa.ewaluacja()
	F = [sum(i) for i in zip(*wartosci)]
	print("Pokolenie %s, stado: %s, średni_argument: %s" % (iteracja, len(Stado_Alfa.stado), (round(F[0]/len(Stado_Alfa.stado),d))),", średnia wartosc f(x) w pokoleniu: ",(round(F[1]/len(Stado_Alfa.stado),d)))

print(max(wartosci, key=itemgetter(1))[0])