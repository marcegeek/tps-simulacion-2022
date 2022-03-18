import numpy as np
import matplotlib.pyplot as plt


def promedio(n):
    prome = []
    for i in range(n):
        prome.append(np.random.randint(0, 36))
    return sum(prome)/len(prome)


def carga_lista(n):
    #lista = []
    #for i in range(n):
    #    lista.append(np.random.randint(0, 36))
    #return lista
    return np.random.randint(0, 36, size=n)


def frecuencia_rel(x):
    # freqs = [(value, x.count(value)/len(x)) for value in set(x)]
    # x es un array de NumPy, comparar tira un array de booleanos (equivalente a 0s y 1s), la suma
    # da la cantidad
    return [(value, (x == value).sum()/len(x)) for value in set(x)]


def main():
    n = 100
    lista = carga_lista(n)
    prom = lista.mean()
    varianza = lista.var()
    desvio = lista.std()
    freqs = frecuencia_rel(lista)
    print(f'El promedio es {prom}')
    print(f'La varianza es {varianza}')
    print(f'El desvío es {desvio}')
    print(freqs)
    #plt.plot(freqs)
    #plt.show()

    # frecuencia relativa, varianza, desvío y promedio


if __name__ == '__main__':
    main()
