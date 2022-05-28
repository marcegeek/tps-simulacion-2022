import numpy as np
from simulacion import Evento, Simulacion


class EventoPartida(Evento):

    def __init__(self, tiempo, callback, servidor):
        super().__init__(tiempo, callback)
        self.servidor = servidor


class ModeloInventario(Simulacion):
    def __init__(self, tasa_arribos, semilla: None):
        super().__init__()
        self.np_randomstate = np.random.RandomState(semilla) ##ver si esto se puede poner en la clase Simulacion
        self.nivel_inventario = 60
        self.area_bajo = 0
        self.area_arriba = 0
        self.orden_arribos(8)
        self.bigs = 40
        self.smalls = 20
        self.costo_incremental = 3
        self.setup_cost = 32
        self.costo_total_orden = 0
        self.tasa_arribos = tasa_arribos ##ver si esto se puede poner en la clase Simulacion

    def orden_arribos(self, cantidad):
        self.nivel_inventario += cantidad
        self.eventos.append(
            Evento(self.reloj + self.np_randomstate.exponential(scale=1 / self.tasa_arribos), self.siguiente)
        )

    def demanda(self, cant_demand):
        self.nivel_inventario -= cant_demand
        self.eventos.append(
            Evento(self.reloj + self.np_randomstate.exponential(scale=1 / self.tasa_arribos), self.siguiente)
        )

    def evaluar(self):
        if self.nivel_inventario < self.smalls:
            cantidad = self.bigs - self.nivel_inventario
            self.costo_total_orden = self.setup_cost + self.costo_incremental * cantidad
            self.eventos.append(
                Evento(self.reloj + self.np_randomstate.exponential(scale=1 / self.tasa_arribos), self.siguiente)
            )

    def reporte(self):
        media_costo_ordenes = self.costo_total_orden /
