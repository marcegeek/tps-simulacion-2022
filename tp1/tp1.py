import numpy as np
import matplotlib.pyplot as plt


"""def promedio(n):
    prome = []
    for i in range(n):
        prome.append(np.random.randint(0, 36))
    return sum(prome)/len(prome)"""


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
    print(f'La lista es: {lista}')
    print(f'El promedio es {prom}')
    print(f'La varianza es {varianza}')
    print(f'El desvío es {desvio}')
    print(freqs)

    fig, ax = plt.subplots()
    ax.plot(range(n), lista)


    ax.plot([0, n], [prom, prom], marker='o')
    #Aquí se grafica la recta del promedio de las tiradas realizadas

    ax.set_title('Promedio de tiradas:', loc = 'left',fontdict = {'fontsize':14, 'fontweight':'bold', 'color':'tab:blue'})
    ax.set_xlabel('Tirada')
    ax.set_ylabel('Número')


    plt.show()
    #Aquí se muestra en una gráfica los distintos números de cada tirada

    ax.plot()

    #plt.plot(freqs)
    #plt.show()

    # frecuencia relativa, varianza, desvío y promedio


if __name__ == '__main__':
    main()
