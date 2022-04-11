import numpy as np
import matplotlib.pyplot as plt
import abc


class Ruleta:
    def __init__(self):
        self.ultimoNumero=None

    def nuevoNumero(self):
        self.ultimoNumero=np.random.randint(0, 37)
        return self.ultimoNumero

    def esNegro(self):
        return self.ultimoNumero in [2,4,6,8,10,11,13,15,17,20,22,24,26,28,29,31,33,35]

    def esRojo(self):
        return self.ultimoNumero!=0 and not self.esNegro()

    def color2int(self):
        return 0 if self.esNegro() else 1 if self.esRojo() else -1


class Jugador:

    def __init__(self, ruleta, capital_inicial, color='rojo'):
        self.ruleta = ruleta
        self.capital = capital_inicial
        self.color = color

    def apostar(self, cantidad):
        self.capital -= cantidad
        gane = self.ruleta.esRojo if self.color == 'rojo' else self.ruleta.esNegro
        if gane():
            self.capital += cantidad * 2
            return True
        else:
            return False


class Estrategia:
    APUESTA_INICIAL = 1
    nombre = 'Estrategia vacía'

    def __init__(self, ruleta, jugador, capital_acotado=True):
        self.ruleta = ruleta
        self.jugador = jugador
        self.cantidad = self.APUESTA_INICIAL
        self.capital_acotado = capital_acotado  # TODO/FIXME algún lugar mejor para la lógica de capital acotado/infinito?

    @abc.abstractmethod
    def avanzar(self):
        pass

    @abc.abstractmethod
    def retroceder(self):
        pass

    def apostar(self):
        if not self.jugador.apostar(self.cantidad):
            self.avanzar()
            if self.capital_acotado:
                if self.jugador.capital < self.cantidad:
                    self.cantidad = self.jugador.capital
            elif self.jugador.capital < self.cantidad:  # capital infinito
                self.jugador.capital = self.cantidad
            return False
        else:
            self.retroceder()
            return True


class EstrategiaMartingala (Estrategia):
    nombre = 'Martingala'

    def avanzar(self):
        self.cantidad *= 2

    def retroceder(self):
        self.cantidad = self.APUESTA_INICIAL


class EstrategiaDAlembert (Estrategia):
    nombre = 'D\'Alembert'

    def avanzar(self):
        self.cantidad += 1

    def retroceder(self):
        self.cantidad = self.APUESTA_INICIAL


class EstrategiaFibonacci(Estrategia):
    nombre = 'Fibonacci'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.generador = self._get_generador()
        self.secuencia = [next(self.generador) for _ in range(10)]
        # inicializar para primer apuesta
        self.index = 1  # empezar como 1 2 3 5 8... en lugar de 1 1 2 3 5 8...

    def avanzar(self):
        self._avanzar(1)

    def retroceder(self):
        self._retroceder(2)

    def _avanzar(self, n):
        self.index += n
        if self.index <= 0:
            self.index = 1  # volver al segundo valor de la sucesión (no repetir dos 1s)
        if self.index >= len(self.secuencia):
            for i in range(self.index - len(self.secuencia) + 1):
                self.secuencia.append(next(self.generador))
        self.cantidad = self.secuencia[self.index] * self.APUESTA_INICIAL

    def _retroceder(self, n):
        self._avanzar(-n)

    @staticmethod
    def _get_generador():
        a, b = 1, 1
        while True:
            yield a
            a, b = b, a + b


def crear_grafica(titulo):
    fig, ax = plt.subplots()
    ax.set_title(titulo, loc='center',
                 fontdict={'fontsize': 14, 'fontweight': 'bold', 'color': 'tab:blue'})
    return fig, ax


def probar_estrategia(estrategia, ruleta, rondas, capital, capital_acotado=True):
    list_est, list_cap, list_num, list_color = [], [], [], []
    victorias, derrotas= 0, 0
    print('')
    print('Usando estrategia: '+estrategia.nombre)
    print('')
    jugador = Jugador(ruleta, capital, color='rojo' if np.random.random()>0.5 else 'negro')
    estrategia = estrategia(ruleta, jugador, capital_acotado=capital_acotado)
    for i in range(rondas):
        ruleta.nuevoNumero()
        list_num.append(ruleta.ultimoNumero)
        list_color.append(ruleta.color2int())
        print(f'Jugador apostará {estrategia.cantidad}')
        estado = 'ganó' if estrategia.apostar() else 'perdió'
        print(f'Jugador {estado}, su capital actual es {jugador.capital}')
        list_est.append(estado)
        list_cap.append(jugador.capital)
        if jugador.capital == 0 and capital!=0:
            print('Jugador quebró')
            break

    for e in list_est:
        if e == "ganó":
            victorias += 1
        else:
            derrotas += 1

    aco = 'acotado' if capital_acotado else 'no acotado'

    list_porc = [victorias, derrotas]
    fig, torta = crear_grafica(f'Gráfico de porcentajes del modelo (capital {aco}):')
    torta.pie(list_porc, labels=["Victorias", "Derrotas"], autopct="%0.1f %%")
    torta.axis("equal")

    fig, cap = crear_grafica(f'Capital en cada ronda ({aco}):')
    cap.plot(range(len(list_cap)), list_cap)

    plt.show()
    return list_cap, list_num, list_color


def frecuencia_rel(x):
    # x es un array de NumPy, comparar tira un array de booleanos (equivalente a 0s y 1s), la suma
    # da la cantidad
    return [x.count(i)/len(x) for i in range(0, max(x)+1)]


def main():
    c_rojo = 0
    c_negro = 0
    c_cero = 0

    numeros, frecuencias, colores = [], [], []
    ruleta = Ruleta()

    t_1_acotado = probar_estrategia(EstrategiaMartingala, ruleta, rondas=1000, capital=10)
    numeros.extend(t_1_acotado[1])
    colores.extend(t_1_acotado[2])
    t_2_acotado = probar_estrategia(EstrategiaDAlembert, ruleta, rondas=1000, capital=10)
    numeros.extend(t_2_acotado[1])
    colores.extend(t_2_acotado[2])
    t_3_acotado = probar_estrategia(EstrategiaFibonacci, ruleta, rondas=1000, capital=10)
    numeros.extend(t_3_acotado[1])
    colores.extend(t_3_acotado[2])

    t_1_infinito = probar_estrategia(EstrategiaMartingala, ruleta, rondas=1000, capital=10, capital_acotado=False)
    numeros.extend(t_1_infinito[1])
    colores.extend(t_1_infinito[2])
    t_2_infinito = probar_estrategia(EstrategiaDAlembert, ruleta, rondas=1000, capital=10, capital_acotado=False)
    numeros.extend(t_2_infinito[1])
    colores.extend(t_2_infinito[2])
    t_3_infinito = probar_estrategia(EstrategiaFibonacci, ruleta, rondas=1000, capital=10, capital_acotado=False)
    numeros.extend(t_3_infinito[1])
    colores.extend(t_3_infinito[2])

    fig, nums = crear_grafica('Frecuencias de aparición por cada número:')
    fig, capi = crear_grafica('Capital por cada Modelo (acotado):')
    fig, colors = crear_grafica('Gráfico de porcentajes de colores:')

    capi.plot(range(len(t_1_acotado[0])), t_1_acotado[0], label="Martingala")
    capi.plot(range(len(t_2_acotado[0])), t_2_acotado[0], label="D'Alembert")
    capi.plot(range(len(t_3_acotado[0])), t_3_acotado[0], label="Fibonacci")
    capi.legend(loc='upper right')

    fig, capi = crear_grafica('Capital por cada Modelo (no acotado):')

    capi.plot(range(len(t_1_infinito[0])), t_1_infinito[0], label="Martingala")
    capi.plot(range(len(t_2_infinito[0])), t_2_infinito[0], label="D'Alembert")
    capi.plot(range(len(t_3_infinito[0])), t_3_infinito[0], label="Fibonacci")
    capi.legend(loc='upper right')

    frecuencias = frecuencia_rel(numeros)

    nums.bar(range(len(frecuencias)), frecuencias)
    nums.set_xlabel('Número')
    nums.set_ylabel('Frecuencia')

    for n in colores:
        if n == 0:
            c_negro += 1
        elif n == 1:
            c_rojo += 1
        else:
            c_cero += 1

    colors.pie([c_negro, c_rojo, c_cero], labels=["Negro", "Rojo", "Cero"], autopct="%0.1f %%")
    colors.axis("equal")

    plt.show()


if __name__ == '__main__':
    main()
