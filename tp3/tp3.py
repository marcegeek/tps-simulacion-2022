import abc
import matplotlib.pyplot as plt
import datetime as dt
import hashlib
import random
import math
import statistics as st
from collections import Counter
from scipy.stats import chisquare


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
    print("La frecuencia es:" + str(abs(z)))
    return "No es aleatorio" if abs(z) > 1.96 else "Puede ser aleatorio"


def poker(l):
    """Bibliografía: https://idoc.pub/documents/idocpub-6klz2po2qvlg"""
    diferentes,un_par,dos_pares,tercia,full,poker,generala=0,0,0,0,0,0,0
    print(l[1])
    for i in range(len(l)):
        digitos=str(l[i]*10**5)[:5]

        counts = Counter(digitos)
        cantidades=[]
        for character, count in counts.most_common():
            if count==5:
                generala +=1
                break
            if count==4:
                poker +=1
                break
            cantidades.append(count)
        if len(cantidades)==5:
            diferentes+=1
        elif len(cantidades)==4:
            un_par+=1
        elif cantidades.count(2)==2:
            dos_pares+=1
        elif len(cantidades)==3: # 3 1 1
            tercia+=1
        elif 3 in cantidades:
            full+=1
    # Frecuencias esperadas.
    fe_dif,fe_unp,fe_dos,fe_res=len(l)*0.3024,len(l)*0.504,len(l)*0.108,len(l)*0.08155
    # 7.815 es el valor "Chi Cuadrado" con p=0.05 y 3 grados de confianza
    return ('No p' if 7.815 > (
        (diferentes-fe_dif)**2/fe_dif
        +(un_par-fe_unp)**2/fe_unp
        +(dos_pares-fe_dos)**2/fe_dos
        +((tercia+full+poker+generala)-fe_res)**2/fe_res
    ) else 'P')+'odemos decir que estos números no vinieron de una distribución uniforme.'


def test_chicuadrado_uniforme(valores, rango, alpha=0.05):
    """Test de chi cuadrado de bondad de ajuste para distribución uniforme discreta"""
    frecs_abs = [valores.count(x) for x in rango]
    frecs_abs_exp = [len(valores)/len(rango)] * len(rango)
    chi2, pvalue = chisquare(frecs_abs, frecs_abs_exp)
    return "No es aleatorio" if pvalue < alpha else "Puede ser aleatorio"


def int2bits(n):
    return [int(i) for i in bin(n)[2:]]


def test_frecuencia(lista):
    """Bibliografia: http://synnick.blogspot.com/2012/03/tarea-3-modelado-y-simulacion.html"""
    # Test de frecuencia (monobit)
    i = 0
    suma = 0
    if min(lista) != 0 or max(lista) != 1:  # lista no es de solo ceros y unos
        # convertir lista de enteros a lista de ceros y unos (extraer sus bits)
        lista_bits = []
        for n in lista:
            lista_bits.extend(int2bits(n))
        lista = lista_bits
    n = len(lista)
    for i in range(len(lista)):
        if lista[i] == 0:
            lista[i] = -1
            suma = suma + lista[i]
    suma_abs = abs(suma)/math.sqrt(n)
    p_value = math.erfc(suma_abs/math.sqrt(2))
    if p_value < 0.01:
        return "No es aleatorio"
    else:
        return "Puede ser aleatorio"


def main():
    """nums = []
    for i in range(8000):
        nums.append(random.random())
    print(poker(nums))
    generador = GCLAnsiC(10)
    nums = []
    for i in range(8000):
        nums.append(generador.rand())
    print(poker(nums))
    return"""

    #Ejemplos de listas no aleatorias y aleatorias testeando con el test de rachas
    lista= [0,1,2,0,1,2,0,1,2,0,1,2,0,1,2,0,1,2,0,1,2,0,1,2,0,1,2,0,1,2,0,1,2,0,1,2]
    lista2=[2,4,2,5,1,6,2]
    print("Lista 1: " + rachas(lista, st.median(lista)))
    print("Lista 2: " + rachas(lista2, st.median(lista2)))

    """Generador GCL AnsiC"""
    generador = GCLAnsiC(10)
    nums = []
    for i in range(8000):
        nums.append(generador.randint(0, 100))
    grafico_puntos(8000, nums)
    grafico_histograma(nums)
    grafico_caja(nums)
    grafico_violin(nums)
    print("Por test de rachas, el generador GCL AsinC: " + rachas(nums, st.median(nums)))
    print("Por test de chi cuadrado, el generador GCL ANSI C: " + test_chicuadrado_uniforme(nums, range(0, 101)))

    """Generador GCL parámetros arbitrarios (m=2**31, a=1000, c=151)"""
    generador = GeneradorGCL(2**31, 1000, 151)
    nums_gcl_arbitrario = generador.randint(0, 100, size=8000)
    grafico_puntos(len(nums_gcl_arbitrario), nums_gcl_arbitrario)
    grafico_histograma(nums_gcl_arbitrario)
    grafico_caja(nums_gcl_arbitrario)
    grafico_violin(nums_gcl_arbitrario)
    print("Por test de rachas, el generador GCL con (m=2**31, a=1000, c=151): " + rachas(nums_gcl_arbitrario, st.median(nums_gcl_arbitrario)))
    print("Por test de chi cuadrado, el generador GCL con (m=2**31, a=1000, c=151): " + test_chicuadrado_uniforme(nums_gcl_arbitrario, range(0, 101)))

    """Generador de Python"""
    nums_python = []
    for i in range(8000):
        nums_python.append(random.randint(0, 100))
    grafico_puntos(8000, nums_python)
    grafico_histograma(nums_python)
    grafico_caja(nums_python)
    grafico_violin(nums_python)
    print("Por test de rachas, el generador MT19937: " + rachas(nums_python, st.median(nums_python)))
    print("Por test de chi cuadrado, el generador MT19937: " + test_chicuadrado_uniforme(nums_python, range(0, 101)))

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
    print("Por test de rachas, el generador de Cuadrados Medios: " + rachas(met_cuad, st.median(met_cuad)))
    print("Por test de chi cuadrado, el generador Cuadrados Medios: " + test_chicuadrado_uniforme(met_cuad, range(0, 10**digitos)))


if __name__ == '__main__':
    main()
