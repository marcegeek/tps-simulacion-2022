import matplotlib.pyplot as plt
import statistics as st
# import numpy as np


class GeneradorGCL:
    """
    Implementación general de un generador congruencial lineal
    """

    def __init__(self, modulo, multiplicador, incremento, semilla):
        self.modulo = modulo
        self.multiplicador = multiplicador
        self.incremento = incremento
        self.valor = semilla
        self._max = modulo - 1

    def _next_raw_int(self):
        self.valor = (self.multiplicador * self.valor + self.incremento) % self.modulo
        return self.valor

    def randint(self, a, b):
        return a + int(self.random() * (b - a) + 0.5)

    def random(self):
        return self._next_raw_int()/self._max


class GCLAnsiC(GeneradorGCL):

    def __init__(self, semilla):
        super().__init__(2**31, 1103515245, 12345, semilla)


class GCLNumericalRecipes(GeneradorGCL):

    def __init__(self, semilla):
        super().__init__(2**32, 1664525, 1013904223, semilla)


class GCLRandu(GeneradorGCL):
    """
    RANDU: un antiguo generador con malas elecciones de parámetros
    """
    def __init__(self, semilla):
        super().__init__(2**31, 65539, 0, semilla)


def grafico_puntos(rango, lista):
    fig, pts = plt.subplots()
    pts.scatter(range(rango), lista)
    plt.show()


def grafico_caja(lista):
    fig, caja = plt.subplots()
    caja.boxplot(lista)
    plt.show()


def grafico_violin(lista):
    fig, viol = plt.subplots()
    viol.violinplot(lista)
    plt.show()


"""def frecuencia_rel(x, valor_max):
    return [(0 if i not in x else x.count(i)/len(x)) for i in range(0, valor_max+1)]


def grafico_frecuencias(lista, valor_max, frec_esperado):
    freqs = frecuencia_rel(lista, valor_max)
    fig, frec_u = plt.subplots()
    frec_u.bar(range(36), freqs)
    frec_u.plot([0, 36], [frec_esperado, frec_esperado], marker='o', linestyle='dotted')
    frec_u.set_title('Frecuencias por número:', loc='center',
                     fontdict={'fontsize': 14, 'fontweight': 'bold', 'color': 'tab:blue'})
    frec_u.set_xlabel('Número')
    frec_u.set_ylabel('Frecuencia')
    plt.show()"""


def grafico_histograma(lista):
    intervalos = range(min(lista), max(lista) + 2)  # calculamos los extremos de los intervalos
    plt.hist(x=lista, bins=intervalos, color='#F2AB6D', rwidth=0.85)
    plt.title('Histograma de números generados')
    plt.xlabel('Número')
    plt.ylabel('Frecuencia')
    plt.xticks(intervalos)
    plt.show()


def main():
    generador = GCLAnsiC(10)
    nums = []
    for i in range(10000):
        nums.append(generador.randint(0, 36))
    print(nums)
    print(nums.count(0)/len(nums))
    print(nums.count(1)/len(nums))

    frec = st.mean(nums)
    grafico_frecuencias(nums, 36, frec)


if __name__ == '__main__':
    main()
