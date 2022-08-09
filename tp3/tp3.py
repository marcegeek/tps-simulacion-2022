import abc
import matplotlib.pyplot as plt
import datetime as dt
import hashlib
import random
import math
import statistics as st
from collections import Counter
from scipy import stats
from chisquare import chisquare  # vieja versión de scipy.stats.chisquare


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


class GeneradorPyMT19937:
    """
    Wrapper para el generador MT19937 de Python
    """

    def __init__(self, semilla=None):
        self._rand_max = 2**32 - 1
        self._random = random.Random(semilla)

    def random(self, size=None):
        def func():
            return self._random.random()

        if size is None:
            return func()
        return [func() for _ in range(size)]

    def randint(self, a, b, size=None):
        def func():
            return self._random.randint(a, b)

        if size is None:
            return func()
        return [func() for _ in range(size)]

    def rand(self, size=None):
        def func():
            return self._random.randint(0, self._rand_max)

        if size is None:
            return func()
        return [func() for _ in range(size)]

    def seed(self, semilla=None):
        self._random.seed(semilla)


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

    #intervalos = range(min(lista), max(lista) + 2)  # calculamos los extremos de los intervalos
    #plt.hist(x=lista, bins=intervalos, color='#F2AB6D', rwidth=0.85)
    plt.hist(lista, bins='sqrt', color='#F2AB6D')
    plt.title('Histograma de números generados')
    plt.xlabel('Número')
    plt.ylabel('Frecuencia absoluta')
    #plt.xticks(intervalos)
    # plt.show()


def grafico_histograma_p(valores_p,nombre_generador):
    #intervalos = range(min(lista), max(lista) + 2)  # calculamos los extremos de los intervalos
    #plt.hist(x=lista, bins=intervalos, color='#F2AB6D', rwidth=0.85)
    # len_valores_p=len(valores_p)
    fig,his=plt.subplots()
    his.hist(valores_p, bins='sqrt', color='#F2AB6D')
    his.set_title('Histograma de números generados - '+nombre_generador)
    his.set_xlabel('Número')
    his.set_ylabel('Frecuencia absoluta')
    # plt.show()


def rachas(l):
    """Bibliografía: https://es.acervolima.com/ejecuta-una-prueba-de-aleatoriedad-en-python/"""
    runs, n1, n2 = 0, 0, 0
    l_median = st.median(l)
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

    if stan_dev == 0:
        return 0.0
    z = (runs - runs_exp) / stan_dev
    pvalue = stats.norm.cdf(-abs(z)) * 2
    return pvalue
    #print("La frecuencia es:" + str(abs(z)))
    #return "No es aleatorio" if abs(z) > 1.96 else "Puede ser aleatorio"


def chi_cuadrado(obs, exp):
    pvalue = chisquare(obs, exp)[1]
    return pvalue


def poker(l):
    """Bibliografía: https://idoc.pub/documents/idocpub-6klz2po2qvlg"""
    diferentes,un_par,dos_pares,tercia,full,poker,generala=0,0,0,0,0,0,0
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
    lenl=len(l)
    # Frecuencias esperadas.
    fe_dif,fe_unp,fe_dos,fe_ter,fe_ful,fe_pok,fe_qui=lenl*0.3024,lenl*0.504,lenl*0.108,lenl*0.072,lenl*0.009,lenl*0.0045,lenl*0.0001
    cantidades_a_tener_en_cuenta=[
        [fe_qui,generala],
        [fe_pok,poker],
        [fe_ful,full],
        [fe_ter,tercia],
        [fe_dos,dos_pares],
        [fe_unp,un_par],
        [fe_dif,diferentes]
    ]
    acumulado=[0,0]
    cantidades_finales=[]
    for cantidad in cantidades_a_tener_en_cuenta:
        if cantidad[1]<5:
            acumulado[0]+=cantidad[0]
            acumulado[1]+=cantidad[1]
        else:
            cantidades_finales.append(cantidad)
    cantidad_de_cantidades_finales=len(cantidades_finales)
    if cantidad_de_cantidades_finales==0:
        return 0.  # Pocos datos, asumimos falla el test -> devolvemos p-value = 0
    if acumulado[0]!=0 and len(cantidades_finales)!=6: # Si solo una fue menor que 5, la ignoramos.
        cantidades_finales.append(acumulado)
    tabla_obs_exp = [
        [],  # valores observados
        []   # valores esperados
    ]
    for exp, obs in cantidades_finales:
        tabla_obs_exp[0].append(obs)
        tabla_obs_exp[1].append(exp)
    # test de chi cuadrado, los grados de libertad se calculan automáticamente
    pvalue = chi_cuadrado(tabla_obs_exp[0], tabla_obs_exp[1])
    return pvalue


def test_chicuadrado_uniforme(valores, rango):
    """Test de chi cuadrado de bondad de ajuste para distribución uniforme discreta"""
    frecs_abs = [valores.count(x) for x in rango]
    frecs_abs_exp = [len(valores)/len(rango)] * len(rango)
    pvalue = chi_cuadrado(frecs_abs, frecs_abs_exp)
    return pvalue


def int2bits(n, maxbits):
    return [int(i) for i in bin(n)[2:].zfill(maxbits)]


def test_frecuencia_monobit(lista):
    """Bibliografia: http://synnick.blogspot.com/2012/03/tarea-3-modelado-y-simulacion.html"""
    # Test de frecuencia (monobit)
    if min(lista) != 0 or max(lista) != 1:  # lista no es de solo ceros y unos
        # convertir lista de enteros a lista de ceros y unos (extraer sus bits)
        maxbits = max(lista).bit_length()
        lista_bits = []
        for n in lista:
            lista_bits.extend(int2bits(n, maxbits))
        lista = lista_bits
    else:  # lista ya es binaria
        lista = lista.copy()
    n = len(lista)
    suma = 0
    for i in range(len(lista)):
        if lista[i] == 0:
            lista[i] = -1
        suma += lista[i]
    suma_abs = abs(suma)/math.sqrt(n)
    p_value = math.erfc(suma_abs/math.sqrt(2))
    return p_value


def evaluar_pvalue(pvalue, alpha=0.05):
    if pvalue <= alpha or abs(pvalue - alpha) < 0.00001:
        return "  NO  "
    else:
        return "QUIZÁS"


def grafico_torta(valores_p1,valores_p0):
    fig,ax = plt.subplots()
    ax.pie(
        [len(valores_p1),len(valores_p0)]
        , labels=["Puede ser aleatorio","No es aleatorio"]
        # , autopct="%0.1f %%"
    )
    #ax.set_title('T´ítulo', loc='center',
     #            fontdict={'fontsize': 14, 'fontweight': 'bold', 'color': 'tab:blue'})
    #ax.plot(range(len(valores_p)), valores_p)


def probar_generador(generador, nombre, n_min=0, n_max=10000, size=1000):
    nums = generador.rand(size=size)  # usar los rangos completos
    valores_p=[]
    #generador.seed()
    rachas_pvalue = rachas(nums)
    chi2_pvalue = test_chicuadrado_uniforme(nums, range(n_min, n_max + 1))
    poker_pvalue = poker(nums)
    frecuencia_monobit_pvalue = test_frecuencia_monobit(nums)
    valores_p.extend([rachas_pvalue,chi2_pvalue,poker_pvalue,frecuencia_monobit_pvalue])
    print(f"| {nombre+' '*(29-len(nombre))} | {evaluar_pvalue(rachas_pvalue)} | {evaluar_pvalue(chi2_pvalue)} | {evaluar_pvalue(poker_pvalue)} | {evaluar_pvalue(frecuencia_monobit_pvalue)} |")
    print('+-------------------------------+--------+--------+--------+--------+')
    # print(nombre)
    #grafico_histograma_p(valores_p,nombre)
    p_evaluados=[evaluar_pvalue(val).startswith('Puede') for val in valores_p]
    #print(p_evaluados)
    #grafico_torta([i for i in range(p_evaluados.count(True))],[i for i in range(p_evaluados.count(False))])


def main():
    """#Ejemplos de listas no aleatorias y aleatorias testeando con el test de rachas
    lista= [0,1,2,0,1,2,0,1,2,0,1,2,0,1,2,0,1,2,0,1,2,0,1,2,0,1,2,0,1,2,0,1,2,0,1,2]
    lista2=[2,4,2,5,1,6,2]
    print("Lista 1: " + evaluar_pvalue(rachas(lista)))
    print("Lista 2: " + evaluar_pvalue(rachas(lista2)))"""

    # Histograma de valores p
    # Test de hipótesis de uniformidad de valores p
        # Por chi cuadrado
    # Proporción de aceptación de hipótesis nula

    print('+-------------------------------+--------+--------+--------+--------+'+'\n'
          '| Generadores pseudoaleatorios  | rachas | chi^2  | poker  | monobit|'+'\n'
          '+-------------------------------+--------+--------+--------+--------+')

    """Generador GCL ANSI C"""
    probar_generador(GCLAnsiC(), "GCL ANSI C")

    """Generador GCL parámetros arbitrarios (m=2**31, a=1000, c=151)"""
    probar_generador(GeneradorGCL(2**31, 1000, 151), "GCL m=2³² a=10³ c=151")

    """Generador de Python"""
    probar_generador(GeneradorPyMT19937(), "MT19937 de Python")

    """Generador Metodos Cuadrados"""
    probar_generador(GeneradorCuadrados(digitos=4), "Cuadrados Medios (4 dígitos)")
    probar_generador(GeneradorCuadrados(digitos=10), "Cuadrados Medios (10 dígitos)")

    plt.show()

if __name__ == '__main__':
    main()
