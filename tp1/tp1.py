import numpy as np
import matplotlib.pyplot as plt
import statistics as st


def carga_lista(n, valor_max):
    return np.random.randint(0, valor_max + 1, size=n)


def frecuencia_rel(x, valor_max):
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
    "Se declaran las listas variables"
    lista, prom, varianza, desvio = [], [], [], []

    "Se declaran las listas a devolver"
    listas, promedios, varianzas, desvios, frecuencias = [], [], [], [], []
    n = 100
    var_esperado = 120
    desv_esperado = 10
    frec_esperado = 0.04
    prom_esperado = 15



    for i in range(10):
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



        promedios.extend(prom)
        listas.extend(lista)
        varianzas.extend(varianza)
        desvios.extend(desvio)
        frecuencias.extend(freqs)

    "Imágen de puntos"
    fig, lis = plt.subplots()
    lis.scatter(range(1000), listas, s=2)
    lis.set_title('Números:', loc='left',
                  fontdict={'fontsize': 14, 'fontweight': 'bold', 'color': 'tab:blue'})
    lis.set_xlabel('Tirada')
    lis.set_ylabel('Número')

    "Imágen de varianza"
    fig, var = plt.subplots()
    var.plot(range(1000), varianzas)
    var.plot([0, 1000], [var_esperado, var_esperado], marker='o', linestyle='dotted')
    var.set_title('Varianzas:', loc='left',
                  fontdict={'fontsize': 14, 'fontweight': 'bold', 'color': 'tab:blue'})
    var.set_xlabel('Tirada')
    var.set_ylabel('Variación')

    "Imágen de frecuencias"
    fig, frec = plt.subplots()
    frec.bar(range(len(frecuencias)), frecuencias)
    frec.plot([0, 1000], [frec_esperado, frec_esperado], marker='o', linestyle='dotted')
    frec.set_title('Frecuencias relativas:', loc='left',
                   fontdict={'fontsize': 14, 'fontweight': 'bold', 'color': 'tab:blue'})
    frec.set_xlabel('Número')
    frec.set_ylabel('Frecuencia')

    "Imágen de desvíos"
    fig, des = plt.subplots()
    des.plot(range(1000), desvios)
    des.plot([0, 1000], [desv_esperado, desv_esperado], marker='|', linestyle='dashed')
    des.set_title('Desvíos:', loc='left',
                  fontdict={'fontsize': 14, 'fontweight': 'bold', 'color': 'tab:blue'})
    des.set_xlabel('Tirada')
    des.set_ylabel('Desvío Estándar')

    "Comienzo de creación de imágen de promedio"
    fig, ax = plt.subplots()
    ax.plot(range(1000), promedios)
    ax.plot([0, 1000], [prom_esperado, prom_esperado], marker='o', linestyle='dotted')
    ax.set_title('Promedio de tiradas:', loc='left',
                 fontdict={'fontsize': 14, 'fontweight': 'bold', 'color': 'tab:blue'})
    ax.set_xlabel('Tirada')
    ax.set_ylabel('Promedio')

    plt.show()


if __name__ == '__main__':
    main()