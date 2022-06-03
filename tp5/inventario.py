from simulacion import Evento, Simulacion


class EventoArriboPedido(Evento):
    def __init__(self, tiempo, callback, cantidad):
        super().__init__(tiempo, callback)
        self.cantidad = cantidad


class ModeloInventario(Simulacion):
    def __init__(self, meses=120, nivel_inventario=60, bigs=40, smalls=20, setup_cost=32, costo_incremental=3,
                 costo_mantenimiento=1, costo_reserva=5, rango_lag=(0.5, 1), media_entredemanda=0.1, distribucion_demanda=((1, 2, 3, 4), (1/6, 1/3, 1/3, 1/6)), semilla=None):
        super().__init__(semilla=semilla)
        self.nivel_inventario = nivel_inventario
        self.meses = meses
        self.bigs = bigs
        self.smalls = smalls
        self.setup_cost = setup_cost
        self.costo_incremental = costo_incremental
        self.costo_mantenimiento = costo_mantenimiento
        self.costo_reserva = costo_reserva
        self.rango_lag = rango_lag
        self.media_entredemanda = media_entredemanda
        self.distribucion_demanda = distribucion_demanda

        self.costo_total_ordenado = 0
        self.mantenidos_area = 0
        self.area_escasez = 0

        self.programar_evaluacion()  # evaluación inicial (inicio primer mes)
        self.programar_demanda()  # demanda inicial

    def programar_evaluacion(self):
        self.eventos.append(Evento(self.reloj + 1, self.evaluar))
        pass

    def programar_arribo_pedido(self, cantidad):
        self.eventos.append(
            EventoArriboPedido(
                self.reloj + self.np_randomstate.uniform(self.rango_lag[0], self.rango_lag[1]),
                self.arribo_pedido,
                cantidad)
        )

    def arribo_pedido(self, ev: EventoArriboPedido):
        self.nivel_inventario += ev.cantidad

    def demanda(self, ev):
        self.programar_demanda()
        valores, distribucion = self.distribucion_demanda
        distribucion_acumulada = [0] + [sum(distribucion[:i]) for i in range(1, len(distribucion) + 1)]
        r = self.np_randomstate.random()
        for i in range(len(distribucion_acumulada) - 1):
            if distribucion_acumulada[i] <= r < distribucion_acumulada[i + 1]:
                break
        # noinspection PyUnboundLocalVariable
        cant_demand = valores[i]
        self.nivel_inventario -= cant_demand

    def programar_demanda(self):
        self.eventos.append(
            Evento(self.reloj + self.np_randomstate.exponential(scale=self.media_entredemanda), self.demanda)
        )

    def evaluar(self, ev):
        if self.nivel_inventario < self.smalls:
            cantidad = self.bigs - self.nivel_inventario
            self.costo_total_ordenado += self.setup_cost + self.costo_incremental * cantidad
            self.programar_arribo_pedido(cantidad)
        self.programar_evaluacion()

    def informe(self):
        costo_ordenes_prom = self.costo_total_ordenado / self.meses
        costo_mantenimiento_prom = self.costo_mantenimiento * self.mantenidos_area / self.meses
        costo_escasez_prom = self.costo_reserva * self.area_escasez / self.meses
        costo_total = costo_ordenes_prom + costo_mantenimiento_prom + costo_escasez_prom
        print(f'Costo orden promedio: {costo_ordenes_prom}')
        print(f'Costo mantenimiento promedio: {costo_mantenimiento_prom}')
        print(f'Costo escasez promedio: {costo_escasez_prom}')
        print(f'Costo total: {costo_total}')

    def actualizar_estadisticas(self):
        super().actualizar_estadisticas()
        if self.nivel_inventario < 0:
            self.area_escasez -= self.nivel_inventario * self.tiempo_desde_ult_evento
        elif self.nivel_inventario > 0:
            self.mantenidos_area += self.nivel_inventario * self.tiempo_desde_ult_evento

    def correr(self):
        while self.reloj < self.meses:
            self.hacer_un_paso()
        self.informe()


def test():
    inventario = ModeloInventario()
    inventario.correr()


if __name__ == '__main__':
    test()
