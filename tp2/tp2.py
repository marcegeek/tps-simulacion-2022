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

    def __init__(self, ruleta, jugador):
        self.ruleta = ruleta
        self.jugador = jugador
        self.cantidad = self.APUESTA_INICIAL

    @abc.abstractmethod
    def apostar(self):
        pass


class EstrategiaMartingala (Estrategia):
    nombre = 'Martingala'

    def apostar(self):
        if not self.jugador.apostar(self.cantidad):
            if self.jugador.capital >= self.cantidad * 2:
                self.cantidad *= 2
            else:
                self.cantidad = self.jugador.capital
            return False
        else:
            self.cantidad = self.APUESTA_INICIAL
            return True


class EstrategiaDAlembert (Estrategia):
    nombre = 'D\'Alembert'

    def apostar(self):
        if not self.jugador.apostar(self.cantidad):
            if self.jugador.capital >= self.cantidad + 1:
                self.cantidad += 1
            else:
                self.cantidad = self.jugador.capital
            return False
        else:
            self.cantidad = self.APUESTA_INICIAL
            return True


class EstrategiaFibonacci(Estrategia):
    nombre = 'Fibonacci'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.generador = self._get_generador()
        self.secuencia = []
        # inicializar para primer apuesta
        self.index = 0
        self._avanzar(0)

    def apostar(self):
        if not self.jugador.apostar(self.cantidad):
            self._avanzar(1)
            if self.jugador.capital < self.cantidad:
                self.cantidad = self.jugador.capital
            return False
        else:
            self._retroceder(2)
            return True

    def _avanzar(self, n):
        self.index += n
        if self.index < 0:
            self.index = 0
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


def probarEstrategia(estrategia,ruleta,rondas,capital):
    list_est, list_cap, list_num, list_color = [], [], [], []
    victorias, derrotas= 0, 0
    print('')
    print('Usando estrategia: '+estrategia.nombre)
    print('')
    jugador = Jugador(ruleta, capital, color='rojo' if np.random.random()>0.5 else 'negro')
    estrategia = estrategia(ruleta, jugador)
    for i in range(rondas):
        ruleta.nuevoNumero()
        list_num.append(ruleta.ultimoNumero)
        list_color.append(ruleta.esNegro())
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


    list_porc = [victorias, derrotas]
    fig, torta = plt.subplots()
    torta.pie(list_porc, labels=["Victorias", "Derrotas"], autopct="%0.1f %%")
    torta.axis("equal")
    torta.set_title('Gráfico de porcentajes del modelo:', loc='center',
                    fontdict={'fontsize': 14, 'fontweight': 'bold', 'color': 'tab:blue'})

    fig, cap = plt.subplots()
    cap.plot(range(len(list_cap)), list_cap)
    cap.set_title('Capital en cada ronda:', loc='center',
                    fontdict={'fontsize': 14, 'fontweight': 'bold', 'color': 'tab:blue'})

    plt.show()
    return list_cap, list_num, list_color

def frecuencia_rel(x):
    # x es un array de NumPy, comparar tira un array de booleanos (equivalente a 0s y 1s), la suma
    # da la cantidad
    return [x.count(i)/len(x) for i in range(0, max(x)+1)]

def main():
    c_rojo = 0
    c_negro = 0

    numeros, frecuencias, colores = [], [], []
    ruleta = Ruleta()

    t_1 = probarEstrategia(EstrategiaMartingala,ruleta,rondas=1000,capital=10)
    numeros.extend(t_1[1])
    colores.extend(t_1[2])
    t_2 = probarEstrategia(EstrategiaDAlembert,ruleta,rondas=1000,capital=10)
    numeros.extend(t_2[1])
    colores.extend(t_2[2])
    t_3 = probarEstrategia(EstrategiaFibonacci,ruleta,rondas=1000,capital=10)
    numeros.extend(t_3[1])
    colores.extend(t_3[2])

    fig, nums = plt.subplots()
    fig, capi = plt.subplots()
    fig, colors = plt.subplots()

    capi.plot(range(len(t_1[0])), t_1[0], label="Martin Gala")
    capi.plot(range(len(t_2[0])), t_2[0], label="DAlembert")
    capi.plot(range(len(t_3[0])), t_3[0], label="Fibonacci")
    capi.legend(loc='upper right')
    capi.set_title('Capital por cada Modelo:', loc='center',
                  fontdict={'fontsize': 14, 'fontweight': 'bold', 'color': 'tab:blue'})

    frecuencias = frecuencia_rel(numeros)

    nums.bar(range(len(frecuencias)), frecuencias)
    nums.set_title('Frecuencias de aparición por cada número:', loc='center',
                     fontdict={'fontsize': 14, 'fontweight': 'bold', 'color': 'tab:blue'})
    nums.set_xlabel('Número')
    nums.set_ylabel('Frecuencia')

    for n in colores:
        if n:
            c_negro += 1
        else:
            c_rojo += 1

    colors.pie([c_negro, c_rojo], labels=["Negro", "Rojo"], autopct="%0.1f %%")
    colors.axis("equal")
    colors.set_title('Gráfico de porcentajes de colores:', loc='center',
                    fontdict={'fontsize': 14, 'fontweight': 'bold', 'color': 'tab:blue'})

    plt.show()



if __name__ == '__main__':
    main()
