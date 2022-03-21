import numpy as np
import matplotlib.pyplot as plt
import statistics as st


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


def carga_list_prom(lista):
    aux, prome = [0], []
    for i in lista:
        aux.append(i)
        prome.append(st.mean(aux))
    return prome


def carga_list_varianza(lista):
    aux, varianza = [0], []
    for i in lista:
        aux.append(i)
        varianza.append(st.variance(aux))
    return varianza


def carga_list_desvio(lista):
    aux, desv = [0], []
    for i in lista:
        aux.append(i)
        desv.append(st.pstdev(aux))
    return desv


def main():
    prom, varianza, desvio = [], [], []
    var_esperado = 120
    desv_esperado = 10
    frec_esperado = 0.04
    prom_esperado = 15


    n = 100
    valor_max = 36
    lista = carga_lista(n, valor_max)
    prom = carga_list_prom(lista)
    varianza = carga_list_varianza(lista)
    desvio = carga_list_desvio(lista)
    freqs = frecuencia_rel(lista, valor_max)
    print(f'La lista es: {lista}')
    print(f'El promedio es {prom}')
    print(f'La varianza es {varianza}')
    print(f'El desvío es {desvio}')
    print(freqs)

    "Imágen de varianza"
    fig, var = plt.subplots()
    var.plot(range(n), varianza)
    var.plot([0, n], [var_esperado, var_esperado], marker='o', linestyle='dotted')
    var.set_title('Varianza:', loc='left',
                 fontdict={'fontsize': 14, 'fontweight': 'bold', 'color': 'tab:blue'})
    var.set_xlabel('Tirada')
    var.set_ylabel('Variación')

    "Imágen de frecuencias"
    fig, frec = plt.subplots()
    frec.bar(range(len(freqs)), freqs)
    frec.plot([0, n], [frec_esperado, frec_esperado], marker='o', linestyle='dotted')
    frec.set_title('Frecuencias relativas:', loc='left',
                   fontdict={'fontsize': 14, 'fontweight': 'bold', 'color': 'tab:blue'})
    frec.set_xlabel('Número')
    frec.set_ylabel('Frecuencia')

    "Imágen de desvíos"
    fig, des = plt.subplots()
    des.plot(range(n), desvio)
    des.plot([0, n], [desv_esperado, desv_esperado], marker='|', linestyle='dashed')
    des.set_title('Desvío estándar:', loc='left',
                 fontdict={'fontsize': 14, 'fontweight': 'bold', 'color': 'tab:blue'})
    des.set_xlabel('Tirada')
    des.set_ylabel('Desvío Estándar')

    "Comienzo de creación de imágen de promedio"
    fig, ax = plt.subplots()
    ax.plot(range(n), prom)

    # Aquí se grafica la recta del promedio de las tiradas realizadas
    ax.plot([0, n], [prom_esperado, prom_esperado], marker='o', linestyle='dotted')

    # Se configuran algunos títulos para mejorar la vista del gráfico
    ax.set_title('Promedio de tiradas:', loc='left', fontdict={'fontsize':14, 'fontweight':'bold', 'color':'tab:blue'})
    ax.set_xlabel('Tirada')
    ax.set_ylabel('Promedio')

    ""

    plt.show()

    # frecuencia relativa, varianza, desvío y promedio


if __name__ == '__main__':
    main()
