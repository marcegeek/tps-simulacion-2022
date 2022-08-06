import abc
import itertools

import numpy as np
import matplotlib.pyplot as plt

from util import stathelper

try:
    from tqdm import tqdm
except ImportError:
    def tqdm(iterator, *args, **kwargs):
        return iterator

from util.plotter import Plot, GraficoDistribucion


class Evento:
    """Clase base evento con callback para la rutina correspondiente"""

    def __init__(self, tiempo, callback):
        self.tiempo = tiempo
        self.callback = callback

    def __lt__(self, other):
        return self.tiempo < other.tiempo

    def __gt__(self, other):
        return self.tiempo > other.tiempo

    def manejar(self):
        self.callback(self)


class Simulacion(abc.ABC):
    """Clase base de una simulación por eventos discretos"""

    # noinspection PyPep8Naming,PyPropertyDefinition
    @staticmethod
    @property
    @abc.abstractmethod
    def NOMBRE_MODELO():
        pass

    def __init__(self, semilla=None):
        self.reloj = 0.
        self.tiempos = [self.reloj]
        self.eventos = []
        self.sig_evento = None  # el valor se modifica en la rutina de avance en el tiempo
        self.tiempo_ult_evento = 0.
        self.tiempo_desde_ult_evento = 0.
        self.np_randomstate = np.random.RandomState(semilla)

    def avance_tiempo(self):
        if len(self.eventos) == 0:
            print(f'Lista de eventos vacía en el tiempo {self.reloj}')
            raise Exception('Lista de eventos vacía')
        self.sig_evento = min(self.eventos)
        self.reloj = self.sig_evento.tiempo
        self.tiempos.append(self.reloj)

    def actualizar_estadisticas(self):
        self.tiempo_desde_ult_evento = self.reloj - self.tiempo_ult_evento
        self.tiempo_ult_evento = self.reloj

    def hacer_un_paso(self):
        self.avance_tiempo()
        self.actualizar_estadisticas()
        self.sig_evento.manejar()
        self.eventos.remove(self.sig_evento)
        self.sig_evento = None

    @abc.abstractmethod
    def es_fin(self):
        pass

    def correr(self, mostrar=False):
        """Relizar una corrida de la simulación"""
        while not self.es_fin():
            self.hacer_un_paso()
        if mostrar:
            self.informe()

    @abc.abstractmethod
    def informe(self):
        pass

    @classmethod
    @abc.abstractmethod
    def medidas_estadisticas(cls):
        """
        Devuelve diccionario con los nombres de cada estadístico y su método como tupla, la clave representa
        el nombre con el que se va a exportar la gráfica respectiva.
        Formato: {'clave': ('nombre estadístico o título de gráfica', cls.metodo), ...}
        """
        pass


class VariadorParametros(abc.ABC):
    """Clase variadora de parámetros, requiere parámetros fijos e iterables (metaparámetros a recorrer)"""

    @abc.abstractmethod
    def get_params(self, *args):
        """Obtener parámetros de la simulación, calculando los valores como fuera necesario"""
        pass

    @property
    def iterables_variacion(self):
        """Obtener la lista de los metaparámetros a iterar con el producto cartesiano"""
        valores = []
        for k in self.__dict__:
            o = self.__dict__[k]
            if hasattr(o, '__getitem__') or hasattr(o, '__iter__'):
                valores.append(o)
        return valores

    @staticmethod
    @abc.abstractmethod
    def obtener_clave(valores):
        """Convertir un conjunto de metaparámetros en una clave apta para identificar gráficas y demás"""
        pass

    @staticmethod
    @abc.abstractmethod
    def descr_parametros(clave):
        """Obtener texto descriptivo de los parámetros"""
        pass

    @staticmethod
    @abc.abstractmethod
    def descr_parametros_graf(clave):
        """Obtener texto descriptivo de los parámetros para gráficas"""
        pass

    def __iter__(self):
        for valores in itertools.product(*self.iterables_variacion):
            yield self.obtener_clave(valores), self.get_params(*valores)


class Experimento:
    """Realizar un experimento con varias corridas de una simulación, variando los parámetros con un variador"""

    def __init__(self, clase, variador_parametros, corridas=10, **kwargs):
        self._clase = clase
        self.parametros = variador_parametros
        self.corridas = corridas
        self.simulaciones = {}
        # instanciar simulaciones, sin correrlas todavía
        for clave, (pargs, pkwargs) in self.parametros:
            # si hay, agregar parámetros fijos de diccionario adicionales
            for k in kwargs:
                pkwargs[k] = kwargs[k]
            self.simulaciones[clave] = [self._clase(*pargs, **pkwargs) for i in range(corridas)]

    def correr(self):
        """Correr las simulaciones del experimento"""
        print('Corriendo simulaciones...')
        for clave in tqdm(self.simulaciones):
            for sim in self.simulaciones[clave]:
                sim.correr()

    def reportar(self, exportar=False, mostrar=True, confianza=0.95):
        for clave in self.simulaciones:
            print()
            print(f"Simulación: {self._clase.NOMBRE_MODELO} - {self.parametros.descr_parametros(clave)}, corridas: {self.corridas}")
            print()
            idx = np.random.randint(0, len(self.simulaciones[clave]) - 1)
            print(f'Resultados corrida n° {idx + 1} (seleccionada al azar):')
            self.simulaciones[clave][idx].informe()
            diccionario_medidas = self._clase.medidas_estadisticas()
            distribuciones = {}
            for k in diccionario_medidas:
                distribuciones[k] = []
            for sim in self.simulaciones[clave]:
                for k in diccionario_medidas:
                    # el método está tomado desde la clase, así que sacamos el nombre y bajamos a la instancia
                    nombre_metodo = diccionario_medidas[k][1].__name__
                    metodo = getattr(sim, nombre_metodo)
                    distribuciones[k].append(metodo())
            print()
            print(f'Resultados experimento:')
            for k in distribuciones:
                if not hasattr(distribuciones[k][0], '__len__'):  # distribución de valores (promedios)
                    promedio_promedios = stathelper.mean(distribuciones[k])
                    desvio_promedios = stathelper.stdev(distribuciones[k])
                    print(f'{diccionario_medidas[k][0]}: {promedio_promedios}, desvío estándar: {desvio_promedios}, IC {int(confianza * 100)}%: {stathelper.intervalo_confianza(distribuciones[k], confianza)}')
                    graf = GraficoDistribucion(f'{diccionario_medidas[k][0]}, {self.parametros.descr_parametros_graf(clave)}')
                    graf.graficar(distribuciones[k])
                    graf.legend()
                else:  # distribución de listas (distribuciones de frecuencia)
                    distribuciones_frec = distribuciones[k]
                    largo_max = max([len(d) for d in distribuciones_frec])
                    probs = [[] for _ in range(largo_max)]
                    for n in range(largo_max):
                        # cargamos las frecuencias obtenidas para cada valor
                        for d in distribuciones_frec:
                            probs[n].append(d[n] if n < len(d) else 0.0)
                    probs_err = [[], []]  # barras de error para las probabilidades
                    for n in range(largo_max):
                        # cambiamos las listas de frecuencia por su medias y obtenemos sus barras de error
                        p = stathelper.mean(probs[n])
                        ic = stathelper.intervalo_confianza(probs[n], confianza)
                        probs[n] = p
                        probs_err[0].append(p - ic[0])
                        probs_err[1].append(ic[1] - p)
                    graf = Plot(f'{diccionario_medidas[k][0]}, {self.parametros.descr_parametros_graf(clave)}',
                                xlabel='Valores', ylabel='Frecuencia relativa')
                    x = np.arange(0, len(probs))
                    graf.bar(x, probs, yerr=probs_err)
                    if len(x) <= 25:
                        graf.ax.set_xticks(x)
                    # noinspection PyUnresolvedReferences
                    intervalos = [(probs[i] - probs_err[0][i], probs[i] + probs_err[1][i]) for i in range(len(probs))]
                    print(f'{diccionario_medidas[k][0]}: {probs}, IC {int(confianza * 100)}%: {intervalos}')
                if exportar:
                    nombre_archivo = f'{clave}_{k}'
                    graf.renderizar(nombre_archivo=nombre_archivo)
                    if not mostrar:
                        plt.close(graf.fig)
            if mostrar:
                plt.show()
