import abc
import itertools
import statistics

import numpy as np
import matplotlib.pyplot as plt

from util.stathelper import intervalo_confianza

try:
    from tqdm import tqdm
except ImportError:
    def tqdm(iterator, *args, **kwargs):
        return iterator

from util.plotter import GraficoDistribucion


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

    def reportar(self, exportar=False, mostrar=True):
        for clave in self.simulaciones:
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
            print(f'Corridas: {len(self.simulaciones[clave])}')
            for k in distribuciones:
                promedio_promedios = statistics.mean(distribuciones[k])
                desvio_promedios = statistics.stdev(distribuciones[k])
                print(f'{diccionario_medidas[k][0]}: promedio de promedios: {promedio_promedios}, desvío estándar: {desvio_promedios}, IC 95%: {intervalo_confianza(distribuciones[k], 0.95)}')
                graf = GraficoDistribucion(f'{diccionario_medidas[k][0]}, {self.parametros.descr_parametros_graf(clave)}')
                graf.graficar(distribuciones[k])
                graf.legend()
                if exportar:
                    nombre_archivo = f'{clave}_{k}'
                    graf.renderizar(nombre_archivo=nombre_archivo)
                    if not mostrar:
                        plt.close(graf.fig)
            if mostrar:
                plt.show()
