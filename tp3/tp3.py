import matplotlib.pyplot as plt


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


def main():
    lista_randint = []
    generador = GCLAnsiC(10)
    nums = []
    for i in range(10000):
        nums.append(generador.randint(0, 36))
    print(nums)
    print(nums.count(0)/len(nums))
    print(nums.count(1)/len(nums))

    """Diagrama de puntos de generador de python"""
    fig, pts = plt.subplots()
    pts.scatter(range(10000), nums)

    """ Diagrama de caja y bigotes"""
    fig, caja = plt.subplots()
    caja.boxplot(nums)

    """Diagrama de violín"""
    fig, viol = plt.subplots()
    viol.violinplot(nums)


    plt.show()


if __name__ == '__main__':
    main()
