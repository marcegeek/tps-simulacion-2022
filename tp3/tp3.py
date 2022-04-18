import abc
import datetime as dt
import hashlib


class Generador(abc.ABC):
    """
    Clase base abstracta general de un generador de números pseudoaleatorios
    """

    def __init__(self, semilla=None):
        self.semilla = None
        self.valor = None
        self.seed(semilla)

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

    def seed(self, semilla=None):
        """
        Inicializar/reinicializar semilla del generador.
        """
        if semilla is None:
            self.semilla = self._guess_seed()
        else:
            self.semilla = semilla
        self.valor = self.semilla

    @abc.abstractmethod
    def _rand(self):
        pass

    @property
    @abc.abstractmethod
    def _rand_max(self):
        pass

    def _guess_seed(self):
        """
        Derivar semilla a partir de la fecha y hora del sistema en microsegundos,
        hasheada con SHA-256 para asegurar la variabilidad
        """
        # en microsegundos para evitar que se repita al inicializar varias veces en poco tiempo
        timestamp = int(dt.datetime.now().timestamp() * 10**6 + .5)
        # hashear el timestamp con SHA-256 para asegurar la variabilidad
        ts_bytes = timestamp.to_bytes(8, 'big')
        sha256 = hashlib.sha256()
        sha256.update(ts_bytes)
        digest = sha256.digest()
        return int.from_bytes(digest, 'big') % (self._rand_max + 1)


class GeneradorGCL(Generador):
    """
    Implementación general de un generador congruencial lineal
    """

    def __init__(self, modulo, multiplicador, incremento, semilla=None):
        self.modulo = modulo
        self.multiplicador = multiplicador
        self.incremento = incremento
        super().__init__(semilla=semilla)  # se llama después porque requiere tener los parámetros cargados

    def _rand(self):
        self.valor = (self.multiplicador * self.valor + self.incremento) % self.modulo
        return self.valor

    @property
    def _rand_max(self):
        return self.modulo - 1


class GCLAnsiC(GeneradorGCL):

    def __init__(self, semilla=None):
        super().__init__(2**31, 1103515245, 12345, semilla=semilla)


class GCLNumericalRecipes(GeneradorGCL):

    def __init__(self, semilla=None):
        super().__init__(2**32, 1664525, 1013904223, semilla=semilla)


class GCLRandu(GeneradorGCL):
    """
    RANDU: un antiguo generador con malas elecciones de parámetros
    """
    def __init__(self, semilla=None):
        super().__init__(2**31, 65539, 0, semilla=semilla)


def test():
    semilla = 10

    generador = GCLAnsiC(semilla)
    print(f'Generando con semilla: {generador.semilla}')
    nums_size = generador.randint(0, 1, size=100)

    generador.seed(semilla)  # resetea con misma semilla
    nums_list = []
    for i in range(len(nums_size)):
        nums_list.append(generador.randint(0, 1))

    assert nums_size == nums_list
    print(nums_size)
    print(nums_size.count(0)/len(nums_size))
    print(nums_size.count(1)/len(nums_size))

    generador.seed()  # obtiene semilla automática
    print(f'Generando con semilla: {generador.semilla}')
    nums = generador.randint(0, 1, size=100)
    print(nums)
    print(nums.count(0)/len(nums))
    print(nums.count(1)/len(nums))


if __name__ == '__main__':
    test()
