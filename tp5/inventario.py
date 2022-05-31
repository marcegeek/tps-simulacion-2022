import numpy as np
from simulacion import Evento, Simulacion


class EventoPartida(Evento):

    def __init__(self, tiempo, callback, servidor):
        super().__init__(tiempo, callback)
        self.servidor = servidor


class ModeloInventario(Simulacion):
    def __init__(self, tasa_arribos, semilla: None):
        super().__init__(semilla=semilla)
        self.nivel_inventario = 60
        self.mantenidos_area = 0
        self.area_escacez = 0
        self.bigs = 40
        self.smalls = 20
        self.costo_incremental = 3
        self.setup_cost = 32
        self.costo_total_ordenado = 0
        self.meses = 120
        self.costo_reserva = 5

        self.costo_mantenimiento = 1
        self.mediana_entredemanda = 0.1

    def orden_arribos(self, cantidad, siguiente):
        self.nivel_inventario += cantidad
        self.costo_total_ordenado += cantidad * self.costo_incremental
        self.eventos.append(
            Evento(self.reloj + self.np_randomstate.exponential(scale=1 / self.mediana_entredemanda), siguiente)
            #El self.siguiente lo agregué porque no sabría que metodo podría agregar al init de Evento
        )

    def demanda(self, cant_demand, siguiente):
        self.nivel_inventario -= cant_demand
        self.eventos.append(
            Evento(self.reloj + self.np_randomstate.exponential(scale=1 / self.mediana_entredemanda), siguiente)
        )

    def evaluar(self, siguiente):
        if self.nivel_inventario < self.smalls:
            cantidad = self.bigs - self.nivel_inventario
            self.costo_total_ordenado = self.setup_cost + self.costo_incremental * cantidad
            self.eventos.append(
                Evento(self.reloj + self.np_randomstate.exponential(scale=1 / self.mediana_entredemanda), siguiente)
            )

    def reporte(self):
        costo_ordenes_prom = self.costo_total_ordenado / self.meses
        costo_mantenimiento_prom = self.costo_mantenimiento * self.mantenidos_area / self.meses
        costo_escacez_prom = self.costo_reserva * self.area_escacez / self.meses
        costo_total = costo_ordenes_prom + costo_mantenimiento_prom + costo_escacez_prom

    def actualizar_estadisticas(self):
        super().actualizar_estadisticas()
        if self.nivel_inventario < 0:
            self.area_escacez -= self.nivel_inventario * self.tiempo_desde_ult_evento
        elif self.nivel_inventario > 0:
            self.mantenidos_area += self.nivel_inventario * self.tiempo_desde_ult_evento
