# Wyznaczanie maksimum funkcji algorytmem ewolucyjnym
# Radosław Majkowski 233256 
# Mateusz Witomski 233270

import os, math
import numpy as np
import random as rand
import matplotlib.pyplot as plt
from collections import Counter

import tkinter as tk
from tkinter import *

import time

import matplotlib

from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure


# funckja przystosowania, wpisana zgodnie z warunkami zadania laboratoryjnego
# uwaga 1: dziedzina funkcji wyklucza zero
# uwaga 2: reguła ruletki nie dopuszcza ujemnych wartości funkcji celu; znamy orientacyjne wartości w interesującyjm przedziale,
# dlatego "podnosimy" wartość o bezpieczne 7

shift = 0 # przesunięcie wartości funkcji w osi Y
iteracja = 0 # wartość startowa, warunek dla iteracja = Gen

def funkcja(argument):
    try:
        y = (math.exp(argument) * math.sin(10*math.pi*argument)+1)/argument
        # y = math.sin(argument) # testowa funkcja kontrolna, w testowym zakresie max=1
    except:
        print("UWAGA! Błąd obliczania wartości funkcji dla argumentu x = %s" % argument) 
        y = 0
    return(y+shift)

# pop_size - liczebność populacji, dobrze, aby była parzysta
pop_size = 150

# Parametry początkowe programu: liczba pokoleń (Gen), liczba zmiennych w funkcji (k), przedział (Xmin, Xmax), dokładność (d)
Gen = 50

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

print("Dla zadanej dokładności i przedziału niezbędne jest zakodowanie %s wartości, użyjemy do tego %s bitów." % (mi, m))


# obsadzamy pierwszą populację o liczebności (pop_size) losowymi wartościami 0/1 wg wyliczonej liczby bitów; pomiędzy chromosoamami nie unikamy powtórzeń
def f_Pokolenie_zero(f_pop_size, f_m, output=False):
    pokolenie_zero = np.random.choice(a=[0, 1], size=(f_pop_size, f_m)) # macierz o rozmiarach: populacja x bitowość, losowo 0/1
    if output: print(*pokolenie_zero, sep = "\n")
    print("Wygenerowano losową populację %s osobników, długość chromosomu: %s." % (f_pop_size, f_m))
    return(pokolenie_zero)

# Sprawdzamy dopasowanie danej populacji, obliczając wartość funkcji dla każdego chromosomu 
# (po dekodowaniu dziesiętnym, dekodowanie2dec)
def f_Ewaluacja(pula, output=False):
    ewaluacja = list() # usunięcie danych z listy do przechowywania wartosci funkcji dla danego pokolenia
    for i in range(pop_size):
        str1 = "".join(map(str, pula[i])) # łączenie elementów listy w string
        #dekodowanie2dec = int(str1, 2) # dekodowanie binarki do liczby dziesiętnej 
        argument = ((Xmax-Xmin)*(int(str1, 2)))/((2**m)-1)+Xmin # mapowanie chromosomu do wartości x z zakresu (Xmin,Xmax)
        wartosc = funkcja(argument) # wartość funkcji w punkcie x
        if wartosc<0: wartosc=0 # wyzerowanie wartości ujemnych; można użyć metody +shift (sztucznie podnieść wartości znanej funkcji) lub korzystać z wartości e^(fx)
        ewaluacja.append([argument, wartosc])  # dodanie wartości do listy
        
    if output:
        print("\nDopasowanie poszczególnych osobników populacji do funkcji celu: ")
        print(*ewaluacja, sep="\n")
        F = [sum(i) for i in zip(*ewaluacja)] #obliczamy dopasowanie całej populacji (F)
        print("Suma dopasowań dla populacji: %s \n" % F[1])
    return(ewaluacja) # zwraca listę krotek argument-wartość dla danej populacji

# Prawdopodobieństwo selekcji (wyboru, Ps) dla każdego chromosomu
# f_Pselekcji() - przyjmuje zestaw wartości funkcji, docelowo wynik działania f_Ewaluacja()
# zwraca - lista wartości z zakresu 0-1, dystrybuanta; niezbędna do działania f_Ruletka() 

def f_Pselekcji(ewaluacja, output=False):
	F = [sum(i) for i in zip(*ewaluacja)] # https://www.geeksforgeeks.org/python-position-summation-in-list-of-tuples/
	Ps=[] # prawdopodobieństwo wyboru (selekcji, Ps) dla każdego chromosomu
	try:
		for x in ewaluacja: Ps.append(x[1]/F[1])
	except:
		print("Błąd obliczania prawdopodobieństw selekcji (Ps).")
	if output: print("Wartosci Ps dla kazdego osobnika: %s"% Ps)
	return(Ps)

# selekcja - metoda koła ruletki (sektory dla Ps)
def f_Ruletka_osobnik(p_selekcji, populacja, output=False):
	ruletka = [] # lista z wartościami początkowymi kolejnych przedziałów ruletki
	sektor = 0 # sektor początkowy, sektory będziemy liczyć od zera: sektor 0: (0,Ps), sektor 1: (Ps[i], Ps+Ps[i+1])

	for i in range(len(p_selekcji)):
		sektor = sektor + p_selekcji[i] 
		ruletka.append(sektor) # dodawanie do listy wartości brzegowej sektora

	if output: print("Koło ruletki: ", *ruletka)

	losowa = rand.random() # losujemy liczbę z przedziału (0,1) tyle razy, ile osobników w populacji
	sektor = 0 # zaczynamy od sektora zero

	for j in range(len(ruletka)): # sprawdzamy, do którego sektora na kole ruletki wpadła wylosowana liczba
		if losowa > ruletka[j]:
			sektor=sektor+1

	if output: print("Losowa liczba %s wpada do sektora %s" % (losowa, sektor))

	# zwracamy osobnika wybranego z puli metodą ruletki:
	return(populacja[sektor])
    
# Krzyżowanie osobników: z puli rodzicielskiej losujemy pop_size/2 par z powtórzeniami
# losujemy losowe_Pc prawdopodobieństwo krzyżowania Pc

def f_Krzyzowanie(parent_1, parent_2, output = False):
    punkt_krzyzowania = rand.randint(1, m-1) # punkt krzyżowania, przecięcie chromosomu najwcześniej za pierwszym bitem, najpóźniej za przedostatnim

    dziecko_1 = np.concatenate((parent_1[:punkt_krzyzowania], parent_2[punkt_krzyzowania:]), axis=None)   
    dziecko_2 = np.concatenate((parent_2[:punkt_krzyzowania], parent_1[punkt_krzyzowania:]), axis=None)
    
    if output: 
        print("Para rodziców: %s x %s, Krzyżowanie po bicie: %s" % (parent_1, parent_2, punkt_krzyzowania))
        print("Para potomków: %s - %s \n" % (dziecko_1, dziecko_2))
    return [dziecko_1, dziecko_2] # lista dla dwóch zwracanych wartości


def f_Mutagen(mutant, output = False): 
    pozycja_mutacji = rand.randint(0, m-1)
    mutant[pozycja_mutacji] = not(mutant [pozycja_mutacji])
    if output: print("Mutacja na pozycji %s:\t %s \n" % (pozycja_mutacji+1, mutant))
    return(mutant)


# f_Pokolenie() - wyznacza kolejną pulę osobników z uwzględnieniem algorytmu genetycznego 
def f_Pokolenie(pula, output = False):

	ewaluacja_pokolenia = f_Ewaluacja(pula, False) # obliczamy wartosci funkcji dla puli osobnikow (jednego pokolenia) (wynik: tablica krotek [x,y])
	prawdopodobienstwo_sel = f_Pselekcji(ewaluacja_pokolenia, False) # obliczamy prawdopodobienstwo selekcji dla poszczegolnych osobnikow (wynik: Ps)

	global iteracja
	global wartosc_srednia_ew

	if output: print("\nPrzetwarzam pokolenie nr %s" % iteracja)
	
	pokolenie_dzieci = []
	numeracja = iter(range(pop_size)) # iterator niezbędny do operacji wewnątrz pętli, przeskok przy krzyżowaniu

	for i in numeracja:
		operacja = rand.random() # tutaj losujemy operację na pokoleniu rodzicow: krzyzowanie lub mutacja lub kopiowanie (wg wytycznych wykładowych)

		rodzic_1 = f_Ruletka_osobnik(prawdopodobienstwo_sel, pula)

		if operacja > (Pc+Pm):
			if output: print("Kopiowanie osobnika: %s" % (rodzic_1))
			pokolenie_dzieci.append(rodzic_1)
		elif operacja > Pm:
			rodzic_2 = f_Ruletka_osobnik(prawdopodobienstwo_sel, pula)
			if output: print("Krzyżowanie osobnikow: %s x %s" % (i, *rodzic_1, *rodzic_2))
			potomstwo = f_Krzyzowanie(rodzic_1, rodzic_2, False)
			try:
				next(numeracja) # próba przeskoczenia iteracji o 2, jeśl się nie uda, do kolejnej puli jest dopisywane tylko jedno "dziecko"
				pokolenie_dzieci.append(potomstwo[0]) # tutaj też jest brzydko, bo mamy na twardo "rodzinę 2+2"
				pokolenie_dzieci.append(potomstwo[1])
			except:
				pokolenie_dzieci.append(potomstwo[0])
		else:
			if output: print("Mutacja osobnika: \t %s" % (rodzic_1))
			pokolenie_dzieci.append(f_Mutagen(f_Ruletka_osobnik(prawdopodobienstwo_sel, pula), False)) # pokolenie_dzieci = f_CMC(pokolenie_rodzicow)
	
	F = [sum(i) for i in zip(*ewaluacja_pokolenia)]
	mean_x = round(F[0]/len(pula),d)
	mean_y = round(F[1]/len(pula),d)
	wartosc_srednia_ew.append([mean_x, mean_y])

	# print("Krotki w pokoleniu:", *ewaluacja_pokolenia, sep="\n")
	# max_xy = list(map(max, zip(*ewaluacja_pokolenia)))
	# #max_xy = ewaluacja_pokolenia[1].index("0")
	# print("Maksymalna krotka w pokoleniu:", max_xy)

	iteracja = iteracja + 1
	
	# rekurencja po zmiennej "iteracja" do zmiennej "Gen" - główna pętla programu
	if iteracja >= Gen:
		print("Przetworzono ostatnie pokolenie nr %s:" % iteracja)
		print("Pokolenie %s, średni_argument: %s \t średnia wartosc f(x) w pokoleniu: %s"% (("{0:0=2d}".format(iteracja)), mean_x, mean_y))
		return(pokolenie_dzieci)
	else:
		print("Pokolenie %s, średni_argument: %s \t średnia wartosc f(x) w pokoleniu: %s"% (("{0:0=2d}".format(iteracja)), mean_x, mean_y))
		return(f_Pokolenie(pokolenie_dzieci))



# uruchomienie obliczen
def form_button():
    global pop_size, Gen, m, Pc, Pm
    global iteracja, wartosc_srednia_ew

    rand.seed()

    # pobieramy wartości wejściowe z formularza
    pop_size = form_pop_size.get()
    Gen = form_gen.get()
    Pc = form_Pcross.get()
    Pm = form_Pmutation.get()

    iteracja = 0
    wartosc_srednia_ew = []
    pierwsze_pokolenie = []

    if (Pc+Pm)<=1:
        print("\nWartości uruchomieniowe: Pop: %s, Gen: %s, Pc: %s, Pm: %s" % (pop_size, Gen, Pc, Pm))

        try:
            pierwsze_pokolenie = f_Pokolenie_zero(pop_size, m) # losujemy osobniki w pierwszym pokoleniu
            print("Utworzono Pokolenie Zero.")
        except:
            print("Nie utworzono Pokolenia Zero!")

        print("guru meditating...")
        start = time.time()
        ostatnie_pokolenie=f_Pokolenie(pierwsze_pokolenie)
        end = time.time()
        
        

        


        form_max_value.set(10)
        form_duration.set("Czas: %s sekund"% round(end-start,3))

        #print("wartosc_srednia_ew ", *wartosc_srednia_ew, sep="\n")
        print("the end: guru's happy!")
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
