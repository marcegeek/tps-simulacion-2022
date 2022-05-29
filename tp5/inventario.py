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
        self.mantenidos_area = 0
        self.area_escacez = 0
        self.orden_arribos(8)
        self.bigs = 40
        self.smalls = 20
        self.costo_incremental = 3
        self.setup_cost = 32
        self.costo_total_ordenado = 0
        self.meses = 120
        self.costo_reserva = 5

        self.costo_mantenimiento = 1
        self.tasa_arribos = tasa_arribos ##ver si esto se puede poner en la clase Simulacion

    def orden_arribos(self, cantidad):
        self.nivel_inventario += cantidad
        self.costo_total_ordenado += cantidad * self.costo_incremental
        self.eventos.append(
            Evento(self.reloj + self.np_randomstate.exponential(scale=1 / self.tasa_arribos),
                   self.siguiente)
            #El self.siguiente lo agregué porque no sabría que metodo podría agregar al init de Evento
        )

    def demanda(self, cant_demand):
        self.nivel_inventario -= cant_demand
        self.eventos.append(
            Evento(self.reloj + self.np_randomstate.exponential(scale=1 / self.tasa_arribos),
                   self.siguiente)
        )

    def evaluar(self):
        if self.nivel_inventario < self.smalls:
            cantidad = self.bigs - self.nivel_inventario
            self.costo_total_ordenado = self.setup_cost + self.costo_incremental * cantidad
            self.eventos.append(
                Evento(self.reloj + self.np_randomstate.exponential(scale=1 / self.tasa_arribos),
                       self.siguiente)
            )

    def reporte(self):
        costo_ordenes_prom = self.costo_total_ordenado / self.meses
        costo_mantenimiento_prom = self.costo_mantenimiento * self.mantenidos_area / self.meses
        costo_escacez_prom = self.costo_reserva * self.area_escacez / self.meses

    def actualizar_estadisticas(self):
        super().actualizar_estadisticas()
        if self.nivel_inventario < 0:
            self.area_escacez -= self.nivel_inventario * self.tiempo_desde_ult_evento
        elif self.nivel_inventario > 0:
            self.mantenidos_area += self.nivel_inventario * self.tiempo_desde_ult_evento
