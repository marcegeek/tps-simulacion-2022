from simulacion import Evento, Simulacion


class EventoPartida(Evento):

    def __init__(self, tiempo, callback, servidor):
        super().__init__(tiempo, callback)
        self.servidor = servidor


class ModeloInventario(Simulacion):
    def __init__(self, meses=120, nivel_inventario=60, bigs=40, smalls=20, setup_cost=32, costo_incremental=3, costo_mantenimiento=1, costo_reserva=5, media_entredemanda=0.1, semilla=None):
        super().__init__(semilla=semilla)
        self.nivel_inventario = nivel_inventario
        self.meses = meses
        self.bigs = bigs
        self.smalls = smalls
        self.setup_cost = setup_cost
        self.costo_incremental = costo_incremental
        self.costo_mantenimiento = costo_mantenimiento
        self.costo_reserva = costo_reserva
        self.media_entredemanda = media_entredemanda

        self.costo_total_ordenado = 0
        self.mantenidos_area = 0
        self.area_escasez = 0

    def orden_arribos(self, cantidad, siguiente):
        self.nivel_inventario += cantidad
        self.costo_total_ordenado += cantidad * self.costo_incremental
        self.eventos.append(
            Evento(self.reloj + self.np_randomstate.exponential(scale=self.media_entredemanda), siguiente)
            #El self.siguiente lo agregué porque no sabría que metodo podría agregar al init de Evento
        )

    def demanda(self, cant_demand, siguiente):
        self.nivel_inventario -= cant_demand
        self.eventos.append(
            Evento(self.reloj + self.np_randomstate.exponential(scale=self.media_entredemanda), siguiente)
        )

    def evaluar(self, siguiente):
        if self.nivel_inventario < self.smalls:
            cantidad = self.bigs - self.nivel_inventario
            self.costo_total_ordenado = self.setup_cost + self.costo_incremental * cantidad
            self.eventos.append(
                Evento(self.reloj + self.np_randomstate.exponential(scale=self.media_entredemanda), siguiente)
            )

    def reporte(self):
        costo_ordenes_prom = self.costo_total_ordenado / self.meses
        costo_mantenimiento_prom = self.costo_mantenimiento * self.mantenidos_area / self.meses
        costo_escacez_prom = self.costo_reserva * self.area_escasez / self.meses
        costo_total = costo_ordenes_prom + costo_mantenimiento_prom + costo_escacez_prom

    def actualizar_estadisticas(self):
        super().actualizar_estadisticas()
        if self.nivel_inventario < 0:
            self.area_escasez -= self.nivel_inventario * self.tiempo_desde_ult_evento
        elif self.nivel_inventario > 0:
            self.mantenidos_area += self.nivel_inventario * self.tiempo_desde_ult_evento
