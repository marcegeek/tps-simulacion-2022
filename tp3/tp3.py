import abc
import matplotlib.pyplot as plt
import datetime as dt
import hashlib
import random
import math
import statistics as st


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
            return self._rand() / (self._rand_max + 1)

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

    def rand(self, size=None):
        """
        Devuelve un entero aleatorio en el rango interno completo del generador.
        O una lista si se especifica el parámetro size.
        """

        def func():
            return self._rand()

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

    def _guess_seed(self):
        """
        Derivar semilla a partir de la fecha y hora del sistema en microsegundos,
        hasheada con SHA-256 para asegurar la variabilidad
        """
        # en microsegundos para evitar que se repita al inicializar varias veces en poco tiempo
        timestamp = int(dt.datetime.now().timestamp() * 10 ** 6 + .5)
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
        super().__init__(2 ** 31, 1103515245, 12345, semilla=semilla)


class GCLNumericalRecipes(GeneradorGCL):

    def __init__(self, semilla=None):
        super().__init__(2 ** 32, 1664525, 1013904223, semilla=semilla)


class GCLRandu(GeneradorGCL):
    """
    RANDU: un antiguo generador con malas elecciones de parámetros
    """

    def __init__(self, semilla=None):
        super().__init__(2 ** 31, 65539, 0, semilla=semilla)


class GeneradorCuadrados(Generador):

    def __init__(self, semilla=None, digitos=4):
        if digitos <= 0 or digitos % 2 != 0:
            raise Exception('La cantidad de dígitos debe ser par')
        self.digitos = digitos
        super().__init__(semilla=semilla)  # se llama después porque requiere tener los parámetros cargados

    def _rand(self):
        numero2 = self.valor ** 2
        snumero2 = str(numero2)
        tam2 = len(snumero2)
        if tam2 < self.digitos * 2:
            snumero2 = '0' * (self.digitos * 2 - tam2) + snumero2
        primerc = self.digitos // 2
        snumero3 = snumero2[primerc:primerc + self.digitos]
        self.valor = int(snumero3)
        return self.valor

    @property
    def _rand_max(self):
        return 10 ** self.digitos - 1


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
    print(nums_size.count(0) / len(nums_size))
    print(nums_size.count(1) / len(nums_size))

    generador.seed()  # obtiene semilla automática
    print(f'Generando con semilla: {generador.semilla}')
    nums = generador.randint(0, 1, size=100)


def grafico_puntos(rango, lista):
    fig, pts = plt.subplots()
    pts.scatter(range(rango), lista)
    pts.set_xlabel('Número de generación')
    pts.set_ylabel('Número aparecido')
    plt.show()


def grafico_caja(lista):
    fig, caja = plt.subplots()
    caja.boxplot(lista)
    caja.set_ylabel('Número')
    plt.show()


def grafico_violin(lista):
    fig, viol = plt.subplots()
    viol.violinplot(lista)
    viol.set_xlabel('Probabilidad de aparición')
    viol.set_ylabel('Número')
    plt.show()


def grafico_histograma(lista):
    intervalos = range(min(lista), max(lista) + 2)  # calculamos los extremos de los intervalos
    plt.hist(x=lista, bins=intervalos, color='#F2AB6D', rwidth=0.85)
    plt.title('Histograma de números generados')
    plt.xlabel('Número')
    plt.ylabel('Frecuencia absoluta')
    plt.xticks(intervalos)
    plt.show()


def rachas(l, l_median):
    """Bibliografía: https://es.acervolima.com/ejecuta-una-prueba-de-aleatoriedad-en-python/"""
    runs, n1, n2 = 0, 0, 0
    for i in range(len(l)):
        if (l[i] >= l_median > l[i - 1]) or \
                (l[i] < l_median <= l[i - 1]):
            runs += 1
        if (l[i]) >= l_median:
            n1 += 1
        else:
            n2 += 1
    runs_exp = ((2 * n1 * n2) / (n1 + n2)) + 1
    stan_dev = math.sqrt((2 * n1 * n2 * (2 * n1 * n2 - n1 - n2)) / \
                         (((n1 + n2) ** 2) * (n1 + n2 - 1)))

    z = (runs - runs_exp) / stan_dev

    return "No es aleatorio" if abs(z) > 1.96 else "Es aleatorio"


def main():
    "Ejemplos de listas no aleatorias y aleatorias testeando con el test de rachas"
    lista= [0,1,2,0,1,2,0,1,2]
    lista2=[2,4,2,5,1,6,2]
    print("Lista 1: " + rachas(sorted(lista), st.median(lista)))
    print("Lista 2: " + rachas(sorted(lista2), st.median(lista2)))

    """Generador GCL AnsiC"""
    generador = GCLAnsiC(10)
    nums = []
    for i in range(8000):
        nums.append(generador.randint(0, 100))
    grafico_puntos(8000, nums)
    grafico_histograma(nums)
    grafico_caja(nums)
    grafico_violin(nums)
    print("Por test de rachas, el generador GCL AsinC: " + rachas(sorted(nums), st.median(nums)))

    """Generador de Python"""
    nums_python = []
    for i in range(8000):
        nums_python.append(random.randint(0, 100))
    grafico_puntos(8000, nums_python)
    grafico_histograma(nums_python)
    grafico_caja(nums_python)
    grafico_violin(nums_python)
    print("Por test de rachas, el generador MT19937: " + rachas(sorted(nums_python), st.median(nums_python)))

    """Generador Metodos Cuadrados"""
    met_cuad = []
    digitos = 4
    semilla = random.randint(0, 10 ** digitos - 1)
    generador = GeneradorCuadrados(semilla=semilla, digitos=digitos)
    print('semilla: ' + str(semilla))
    print("Cantidad de dígitos: ", digitos)
    for i in range(100):
        met_cuad.append(generador.rand())

    grafico_puntos(100, met_cuad)
    plt.hist(met_cuad, bins='sqrt')
    grafico_caja(met_cuad)
    grafico_violin(met_cuad)
    print("Por test de rachas, el generador de Cuadrados Medios: " + rachas(sorted(met_cuad), st.median(met_cuad)))


if __name__ == '__main__':
    main()
