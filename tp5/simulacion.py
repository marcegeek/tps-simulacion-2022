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


class Simulacion:
    """Clase base de una simulación por eventos discretos"""

    def __init__(self):
        self.reloj = 0.
        self.eventos = []
        self.sig_evento = None  # el valor se modifica en la rutina de avance en el tiempo
        self.tiempo_ult_evento = 0.
        self.tiempo_desde_ult_evento = 0.

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
