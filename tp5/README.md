# Especificaciones del sistema de colas:
## Intervalo entre arribos:
Variar en 25%, 50%, 75%, 100%, 125% de la tasa de servicio. 

## Duración del servicio:
~Exp(0.5 cliente/min): valor esperado 2'

## Tamaño de cola:
Variar: Infinita, 0, 2, 5, 10, 50

## Criterio de finalizado:
n = 1000

# Especificaciones del sistema de inventario:
## Período:
1 mes

## Intervalo entre demandas:
~Exp(1/0.1 mes): valor esperado 0.1 mes

## Tamaños de las demandas:
~Empírica:
- 1 c.p. 1/6
- 2 c.p. 1/3
- 3 c.p. 1/3
- 4 c.p. 1/6

## Política de reposición:
Estacionaria.

Z =
- S-I si I \< s
- 0 si I >= s
Variar S y s entre:

![image](https://user-images.githubusercontent.com/51477979/170153570-15b17e73-9aa2-4651-aef5-31597cb73104.png)

## Inventario inicial
I(0) = 60
  
## Tardanza de la reposición:
~Unif(0.5 mes, 1 mes)
  
## Criterio de finalización:
t = 120

## Costo inicial de envío:
K = 32 si Z > 0, sino 0.

## Costo incremental de envío:
i = 3

## Costo de mantenimiento por período:
h = 1

## Costo de pérdida por no cumplir demanda por período:
π = 5
