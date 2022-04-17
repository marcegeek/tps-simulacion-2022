import abc


class Generador(abc.ABC):
    """
    Clase base abstracta general de un generador de números pseudoaleatorios
    """

    def random(self, size=None):
        """
        Devuelve un flotante aleatorio en el intervalo semiabierto [0, 1).
        O una lista si se especifica el parámetro size.
        """
        def func():
            return self._rand()/(self._rand_max + 1)
        if size is None:
            return func()
        return [func() for _ in range(size)]

    def randint(self, a, b, size=None):
        """
        Devuelve un entero aleatorio en el rango [a, b], incluyendo los extremos.
        O una lista si se especifica el parámetro size.
        """
        def func():
            # código basado en http://c-faq.com/lib/randrange.html
            return a + self._rand() // (self._rand_max // (b - a + 1) + 1)
        if size is None:
            return func()
        return [func() for _ in range(size)]

    @abc.abstractmethod
    def _rand(self):
        pass

    @property
    @abc.abstractmethod
    def _rand_max(self):
        pass


class GeneradorGCL(Generador):
    """
    Implementación general de un generador congruencial lineal
    """

    def __init__(self, modulo, multiplicador, incremento, semilla):
        self.modulo = modulo
        self.multiplicador = multiplicador
        self.incremento = incremento
        self.valor = semilla

    def _rand(self):
        self.valor = (self.multiplicador * self.valor + self.incremento) % self.modulo
        return self.valor

    @property
    def _rand_max(self):
        return self.modulo - 1


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
    semilla = 10

    generador = GCLAnsiC(semilla)
    nums_size = generador.randint(0, 1, size=100)

    generador = GCLAnsiC(semilla)
    nums_list = []
    for i in range(len(nums_size)):
        nums_list.append(generador.randint(0, 1))
    print(nums_size)
    print(nums_size.count(0)/len(nums_size))
    print(nums_size.count(1)/len(nums_size))
    assert nums_size == nums_list


if __name__ == '__main__':
    main()
