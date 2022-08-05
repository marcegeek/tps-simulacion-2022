import statistics as st
from scipy import stats


def intervalo_confianza(valores, confianza=0.95):
    """
    Obtener el intervalo de confianza para un conjunto de valores distribuidos de manera centrada.
    Asumiendo una distribución normal para una cantidad de elementos n >= 30, o una t de Student si n < 30
    """
    media, desvio = st.mean(valores), st.stdev(valores)
    if desvio == 0.0:
        return media, media
    if len(valores) >= 30:  # al menos 30 elementos, usar distribución normal
        dist = stats.norm(loc=media, scale=desvio)
    else:  # menos de 30 elementos, usar distribución t de Student con n - 1 grados de libertad
        dist = stats.t(len(valores) - 1, loc=media, scale=desvio)
    return dist.interval(confianza)
