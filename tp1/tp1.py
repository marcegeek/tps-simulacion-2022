import numpy as np
import matplotlib.pyplot as plt


"""def promedio(n):
    prome = []
    for i in range(n):
        prome.append(np.random.randint(0, 36))
    return sum(prome)/len(prome)"""


def carga_lista(n, valor_max):
    #lista = []
    #for i in range(n):
    #    lista.append(np.random.randint(0, 36))
    #return lista
    return np.random.randint(0, valor_max + 1, size=n)


def frecuencia_rel(x, valor_max):
    # freqs = [(value, x.count(value)/len(x)) for value in set(x)]
    # x es un array de NumPy, comparar tira un array de booleanos (equivalente a 0s y 1s), la suma
    # da la cantidad
    return [(x == value).sum()/len(x) for value in range(0, valor_max + 1)]


def main():
    n = 100
    valor_max = 36
    lista = carga_lista(n, valor_max)
    prom = lista.mean()
    varianza = lista.var()
    desvio = lista.std()
    freqs = frecuencia_rel(lista, valor_max)
    print(f'La lista es: {lista}')
    print(f'El promedio es {prom}')
    print(f'La varianza es {varianza}')
    print(f'El desvío es {desvio}')
    print(freqs)

    "Comienzo de creación de imágen de promedio"
    fig, ax = plt.subplots()
    ax.plot(range(n), lista)

    # Aquí se grafica la recta del promedio de las tiradas realizadas
    ax.plot([0, n], [prom, prom], marker='o')

    # Se configuran algunos títulos para mejorar la vista del gráfico
    ax.set_title('Promedio de tiradas:', loc = 'left',fontdict = {'fontsize':14, 'fontweight':'bold', 'color':'tab:blue'})
    ax.set_xlabel('Tirada')
    ax.set_ylabel('Número')

    plt.show()

    "Comienzo de imágen de frecuencias relativas"
    fig, frec = plt.subplots()
    frec.bar(range(len(freqs)), freqs)
    frec.set_title('Frecuencias relativas:',loc='left',fontdict={'fontsize': 14, 'fontweight': 'bold', 'color': 'tab:blue'})
    frec.set_xlabel('Número')
    frec.set_ylabel('Frecuencia')
    plt.show()

    # frecuencia relativa, varianza, desvío y promedio


if __name__ == '__main__':
    main()
