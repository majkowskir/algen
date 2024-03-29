# Wyznaczanie maksimum funkcji algorytmem ewolucyjnym
# Radosław Majkowski 233256 
# Mateusz Witomski 233270

import time, math, matplotlib
import matplotlib.pyplot as plt

import numpy as np
import random as rand

from collections import Counter

from operator import itemgetter

import tkinter as tk
from tkinter import *

# funckja przystosowania, wpisana zgodnie z warunkami zadania laboratoryjnego
# uwaga 1: dziedzina funkcji wyklucza zero
# uwaga 2: reguła ruletki nie dopuszcza ujemnych wartości funkcji celu; znamy orientacyjne wartości w interesującyjm przedziale,
# dlatego "podnosimy" wartość o bezpieczne 7

iteracja = 0 # wartość startowa, warunek dla iteracja = Gen

# Parametry początkowe programu: liczba pokoleń (Gen), liczba zmiennych w funkcji (k), przedział (Xmin, Xmax), dokładność (d)
Gen = 5

# pop_size - liczebność populacji, dobrze, aby była parzysta
pop_size = 5
# prawdopodobieństwa: krzyżowania (Pc) oraz mutacji (Pm)
Pc = 0.25
Pm = 0.01

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

	def crossover(self, rodzic_1, rodzic_2):
		punkt_krzyzowania = rand.randint(1, m-2) # punkt krzyżowania, przecięcie chromosomu najwcześniej za pierwszym bitem, najpóźniej za przedostatnim
		try:
			dziecko_1 = np.concatenate((rodzic_1[:punkt_krzyzowania], rodzic_2[punkt_krzyzowania:]), axis=None)   
			dziecko_2 = np.concatenate((rodzic_2[:punkt_krzyzowania], rodzic_1[punkt_krzyzowania:]), axis=None)
		except:
			print("blad krzyzowania")
		return (dziecko_1, dziecko_2)


class Populacja:
	
	def __init__(self, liczebnosc_stada):
		self.stado = []
		for i in range(liczebnosc_stada):
			self.stado.append(Osobnik())

	# metoda oblicza wartości funkcji dla danej populacji przedstawionej w postaci binarnej
	def ewaluacja(self):
		wartosci_f = [] # usunięcie danych z listy do przechowywania wartosci funkcji dla danego pokolenia
		for i in range(len(self.stado)):
			my_lst = self.stado[i].chromosom
			str1=""
			str1 = "".join(map(str, my_lst)) # łączenie elementów listy w string
			dekodowanie2dec = int(str1, 2) # dekodowanie binarki do liczby dziesiętnej 
			argument = ((Xmax-Xmin)*dekodowanie2dec)/((2**m)-1)+Xmin # mapowanie chromosomu do wartości x z zakresu (Xmin,Xmax)
			wartosc = funkcja(argument) # wartość funkcji w punkcie x 
			if wartosc < 0: wartosc = 0 # zapewniamy dla ruletki wartości dodatnie przez wyzerowanie ujemnych
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
			print("suma prawdopodobieństw wynosi zero?!?")

		sektor = 0
		kolo_ruletki = []
		for i in range(len(Ps)):
			sektor = sektor + Ps[i]
			kolo_ruletki.append(sektor) # dodawanie wartości brzegowej sektora do listy


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
			
			# KOPIOWANIE
			if operacja > (Pc+Pm):
				try:
					potomstwo.append(self.ruletka())
				except:
					print("Błąd kopiowania!")
			
			# KRZYZOWANIE
			elif operacja > Pm:
				rodzic_1 = self.ruletka()
				rodzic_2 = self.ruletka()
				dzieci = self.stado[i].crossover(rodzic_1, rodzic_2)
				
				try:
					next(iteracja)
					potomstwo.append(dzieci[0]) # tu jest brzydko, bo na twardo
					potomstwo.append(dzieci[1])
				except:
					potomstwo.append(dzieci[0]) # jeśli krzyzujemy ostatniego osobnika w puli, propagowane jest tylko jedno dziecko
			
			# MUTACJA
			else:
				pozycja_mutacji = rand.randint(0, m-1)
				rodzic_1 = self.ruletka()
				rodzic_1[pozycja_mutacji]=abs(rodzic_1[pozycja_mutacji]-1)
				mutant = rodzic_1
				potomstwo.append(mutant)

		# przepisanie stada rodzicielskiego na potomne:
		for i in (range(len(potomstwo))): 
			#print(i,self.stado[i].chromosom," ",potomstwo[i])
			potomek = potomstwo[i]
			self.stado[i].chromosom = potomek
		return(potomstwo)

 

# wypisanie osobników w stadzie A
#for i in range(pop_size):
#	print(Stado_Alfa.stado[i].chromosom)

# GŁÓWNA PĘTLA PROGRAMU
# for iteracja in range(Gen):	
# 	wartosci = Stado_Alfa.ewaluacja()
# 	#print(*wartosci, sep="\n")
# 	Stado_Alfa.operacje()
# 	F = [sum(i) for i in zip(*wartosci)] # suma wartości funkcji jaką uzyskujemy ze wszystkich osobników w populacji
# 	mean_X = (round(F[1]/len(Stado_Alfa.stado),d)) # średnia wartość funkcji w danym pokoleniu
# 	print("Pokolenie %s, średni_argument: %s\t" % (("{0:0=2d}".format(iteracja)), (round(F[0]/len(Stado_Alfa.stado),d))),", średnia wartosc f(x) w pokoleniu: \t", mean_X)
	
# max_X = round((max(wartosci, key=itemgetter(1))[0]),d)
# print("\nWartosc argumentu dającego maksymalną wartość funkcji w ostatnim pokoleniu: ", max_X)
# print("Wartość funkcji: ", round(funkcja(max_X),d))


def form_button():
	global pop_size, Gen, m, Pc, Pm
	global iteracja, wartosc_srednia_ew

	rand.seed()
	
	# utworzenie stada A
	Stado_Alfa = Populacja(pop_size)

	# pobieramy wartości wejściowe z formularza
	pop_size = form_pop_size.get()
	Gen = form_gen.get()
	Pc = form_Pcross.get()
	Pm = form_Pmutation.get()

	print("\nDla zadanej dokładności i przedziału \nniezbędne jest zakodowanie minimum %s wartości,\nużyjemy do tego %s bitów.\n" % (mi, m))
	print("Wartości uruchomieniowe:\nPopulacja: %s, Gen: %s, Pc: %s, Pm: %s\n" % (pop_size, Gen, Pc, Pm))

	iteracja = 0
	wartosc_srednia_ew=list()
	pierwsze_pokolenie=list()
	if (Pc+Pm)<=1:
		for iteracja in range(Gen):
			
			wartosci = Stado_Alfa.ewaluacja()
			#print(*wartosci, sep="\n")
			Stado_Alfa.operacje()
			F = [sum(i) for i in zip(*wartosci)] # suma wartości funkcji jaką uzyskujemy ze wszystkich osobników w populacji
			mean_X = (round(F[1]/len(Stado_Alfa.stado),d)) # średnia wartość funkcji w danym pokoleniu
			print("Pokolenie %s, średni_argument: %s\t" % (("{0:0=2d}".format(iteracja)), (round(F[0]/len(Stado_Alfa.stado),d))),", średnia wartosc f(x) w pokoleniu: \t", mean_X)
		
		max_X = round((max(wartosci, key=itemgetter(1))[0]),d)
		print("\nWartosc argumentu dającego maksymalną wartość funkcji w ostatnim pokoleniu: ", max_X)
		print("Wartość funkcji: ", round(funkcja(max_X),d))
	else:
		messagebox.showinfo("Błąd wprowadzonych wartości P", "Suma prawdopodobieństw krzyżowania i mutacji nie może przekroczyć 1")



root=tk.Tk()

root.title("Laboratorium 3: Algorytm genetyczny, wyznaczanie max funkcji. R.Majkowski (233256), M. Witomski (233270)")
root.configure(bg='white', padx=20, pady=20)

form_pop_size = IntVar()
form_pop_size.set(pop_size)
tk.Entry(root, bg="white", textvariable=form_pop_size).grid(row=0, column=0, padx=10, sticky=tk.W)
tk.Label(root, text="Liczba osobników: ", bg="white", padx = 10).grid(row=1, column=0, padx=10, sticky=tk.W)

form_gen = IntVar()
form_gen.set(Gen)
tk.Entry(root, bg="white", textvariable=form_gen).grid(row=0, column=1, padx=10, sticky=tk.W)
tk.Label(root, text="Liczba pokoleń: ", bg="white", padx = 10).grid(row=1, column=1, padx=10, sticky=tk.W)

form_Pcross = DoubleVar()
form_Pcross.set(Pc)
tk.Entry(root, bg="white", textvariable=form_Pcross).grid(row=0, column=2, padx=10, sticky=tk.W)
tk.Label(root, text="P. krzyżowania: ", bg="white", padx = 10).grid(row=1, column=2, padx=10, sticky=tk.W)

form_Pmutation = DoubleVar()
form_Pmutation.set(Pm)
tk.Entry(root, bg="white", textvariable = form_Pmutation).grid(row=0, column=3, padx=10, sticky=tk.W)
tk.Label(root, text="P. mutacji: ", bg = "white", padx = 10).grid(row=1, column=3, padx=10, sticky=tk.W)

tk.Button(text="Uruchom", command = form_button).grid(row=0, column=4, padx=10, sticky=tk.W)

form_max_value = DoubleVar() # testowa kontrolka dla dowolnej wartości
form_max_value.set(0)
tk.Label(root, textvariable=form_max_value, bg="white").grid(row=2, column=0, padx=10, sticky=tk.W)

form_duration = DoubleVar() 
form_duration.set(0)
tk.Label(root, textvariable=form_duration, bg="white").grid(row=3, column=0, padx=10, sticky=tk.W)

# wykres.create_text(200, 20,fill="darkblue",font="Times 12 italic bold", tex = vtext)
# wykres.create_line(0, 0, 200, 100)

root.mainloop()


