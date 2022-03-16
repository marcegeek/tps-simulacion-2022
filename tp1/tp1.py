import numpy as np


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


def main():
    n = 100
    lista = carga_lista(n)
    prom = lista.mean()
    varianza = lista.var()
    desvio = lista.std()
    print(f'El promedio es {prom}')
    print(f'La varianza es {varianza}')
    print(f'El desvío es {desvio}')

    # frecuencia relativa, varianza, desvío y promedio


if __name__ == '__main__':
    main()
