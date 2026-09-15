
"""Transformaciones del preprocesado del TFM que no tienen equivalente
en scikit-learn. Acompaña al modelo serializado."""

import numpy as np


def tramificar(X, cortes):
    """Asigna cada valor al índice del intervalo que le corresponde.

    X:      matriz (n_filas, n_columnas)
    cortes: lista de arrays, uno por columna, con los cortes interiores
    """
    return np.column_stack([
        np.digitize(X[:, i], bins=c) for i, c in enumerate(cortes)
    ])
