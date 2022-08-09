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

    fig, var_u = plt.subplots()
    fig, frec_u = plt.subplots()
    fig, des_u = plt.subplots()
    fig, ax_u = plt.subplots()

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

        var_u.plot(range(100), varianza)
        var_u.plot([0, 100], [var_esperado, var_esperado], marker='o', linestyle='dotted')
        var_u.set_title('Varianzas por tiradas:', loc='center',
                      fontdict={'fontsize': 14, 'fontweight': 'bold', 'color': 'tab:blue'})
        var_u.set_xlabel('Tirada')
        var_u.set_ylabel('Variación')

        "Imágen de frecuencias"
        frec_u.bar(range(37), freqs)
        frec_u.plot([0, 36], [frec_esperado, frec_esperado], marker='o', linestyle='dotted')
        frec_u.set_title('Frecuencias por número:', loc='center',
                       fontdict={'fontsize': 14, 'fontweight': 'bold', 'color': 'tab:blue'})
        frec_u.set_xlabel('Número')
        frec_u.set_ylabel('Frecuencia')

        "Imágen de desvíos"
        des_u.plot(range(100), desvio)
        des_u.plot([0, 100], [desv_esperado, desv_esperado], marker='|', linestyle='dashed')
        des_u.set_title('Desvío por tiradas:', loc='center',
                      fontdict={'fontsize': 14, 'fontweight': 'bold', 'color': 'tab:blue'})
        des_u.set_xlabel('Tirada')
        des_u.set_ylabel('Desvío Estándar')

        "Comienzo de creación de imágen de promedio"
        ax_u.plot(range(100), prom)
        ax_u.plot([0, 100], [prom_esperado, prom_esperado], marker='o', linestyle='dotted')
        ax_u.set_title('Promedio por tirada:', loc='center',
                     fontdict={'fontsize': 14, 'fontweight': 'bold', 'color': 'tab:blue'})
        ax_u.set_xlabel('Tirada')
        ax_u.set_ylabel('Promedio')

        promedios.extend(prom)
        listas.extend(lista)
        varianzas.extend(varianza)
        desvios.extend(desvio)
        frecuencias.extend(freqs)
    plt.show()

    "Imágen de puntos"
    fig, lis = plt.subplots()
    lis.scatter(range(1000), listas, s=2)
    lis.set_title('Números aparecidos:', loc='left',
                  fontdict={'fontsize': 14, 'fontweight': 'bold', 'color': 'tab:blue'})
    lis.set_xlabel('Tirada')
    lis.set_ylabel('Número')

    "Imágen de varianza"
    fig, var = plt.subplots()
    var.plot(range(1000), varianzas)
    var.plot([0, 1000], [var_esperado, var_esperado], marker='o', linestyle='dotted')
    var.set_title('Varianza promedio:', loc='left',
                  fontdict={'fontsize': 14, 'fontweight': 'bold', 'color': 'tab:blue'})
    var.set_xlabel('Tirada')
    var.set_ylabel('Variación')


    "Imágen de desvíos"
    fig, des = plt.subplots()
    des.plot(range(1000), desvios)
    des.plot([0, 1000], [desv_esperado, desv_esperado], marker='|', linestyle='dashed')
    des.set_title('Desvío promedio:', loc='left',
                  fontdict={'fontsize': 14, 'fontweight': 'bold', 'color': 'tab:blue'})
    des.set_xlabel('Tirada')
    des.set_ylabel('Desvío Estándar')

    "Comienzo de creación de imágen de promedio"
    fig, ax = plt.subplots()
    ax.plot(range(1000), promedios)
    ax.plot([0, 1000], [prom_esperado, prom_esperado], marker='o', linestyle='dotted')
    ax.set_title('Promedio global:', loc='left',
                 fontdict={'fontsize': 14, 'fontweight': 'bold', 'color': 'tab:blue'})
    ax.set_xlabel('Tirada')
    ax.set_ylabel('Promedio')

    plt.show()


if __name__ == '__main__':
    main()