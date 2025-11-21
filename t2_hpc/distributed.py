import numpy as np
from mpi4py import MPI
from numba import njit, prange, config
import numpy.linalg as la

# Inicialización de MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

def generate_distributed_data(ntotal, d, k, seed):
    # Genera datos distribuidos localmente en cada proceso
    # Retorna: arreglo local de datos (n_local, d)
    n_local = ntotal // size
    rng = np.random.default_rng(seed + rank)

    centers = rng.normal(loc=0.0, scale=5.0, size=(k, d))
    choices = rng.integers(0, k, size=n_local)
    local_data = np.empty((n_local, d), dtype=np.float64)

    for i in range(n_local):
        c = choices[i]
        local_data[i, :] = centers[c] + rng.normal(0.0, 1.0, size=d)

    return local_data


@njit(parallel=True)
def compute_distances(data, centroids):
    # Calcula distancias euclidianas entre puntos y centroides con prange
    # Retorna: matriz de distancias (n_local, k)
    n_local = data.shape[0]
    k = centroids.shape[0]
    d = data.shape[1]
    distances = np.empty((n_local, k), dtype=np.float64)
    for i in prange(n_local):
        for j in range(k):
            s = 0.0
            for l in range(d):
                diff = data[i, l] - centroids[j, l]
                s += diff * diff
            distances[i, j] = np.sqrt(s)
    return distances


@njit(parallel=True)
def assign_labels(distances):
    # Asigna cada punto al cluster más cercano
    # Retorna: arreglo de etiquetas (n_local, 
    n_local = distances.shape[0]
    k = distances.shape[1]
    labels = np.empty(n_local, dtype=np.int64)
    for i in prange(n_local):
        best = 0
        best_d = distances[i, 0]
        for j in range(1, k):
            if distances[i, j] < best_d:
                best = j
                best_d = distances[i, j]
        labels[i] = best
    return labels


@njit(parallel=True)
def compute_local_sums(data, labels, k):
    # Acumula sumas parciales por cluster
    # Retorna: tupla (sumas_por_cluster, conteos_por_cluster)
    n_local = data.shape[0]
    d = data.shape[1]
    sums = np.zeros((k, d), dtype=np.float64)
    counts = np.zeros(k, dtype=np.int64)
    for i in prange(n_local):
        lab = labels[i]
        counts[lab] += 1
        for j in range(d):
            sums[lab, j] += data[i, j]
    return sums, counts


def kmeans_distributed(data, k, max_iters=100, tol=1e-4):
    # 1. Inicializar centroides (solo en rank 0)
    # 2. Bucle principal:
    #    a. Distribuir centroides con comm.Bcast
    #    b. Calcular distancias y asignar etiquetas localmente
    #    c. Calcular sumas parciales
    #    d. Reducir sumas globales con comm.Allreduce(..., op=MPI.SUM)
    #    e. Actualizar centroides (solo rank 0)
    #    f. Verificar convergencia
    # 3. Retornar centroides finales y etiquetas
    d = data.shape[1]

    # Inicializar centroides en rank 0
    if rank == 0:
        rng = np.random.default_rng(0)
        n_local = data.shape[0]
        if n_local >= k:
            # tomar k puntos aleatorios del rank 0 (si es posible)
            idx = rng.choice(n_local, size=k, replace=False)
            centroids = data[idx].astype(np.float64).copy()
        else:
            # si rank 0 no tiene suficientes puntos, genera centroides aleatorios
            centroids = rng.normal(0.0, 1.0, size=(k, d)).astype(np.float64)
    else:
        # reservar espacio para recibir broadcast
        centroids = np.empty((k, d), dtype=np.float64)

    # Broadcast inicial
    comm.Bcast(centroids, root=0)

    labels = None
    for it in range(max_iters):
        # 1) cada proceso calcula distancias y labels localmente
        distances = compute_distances(data, centroids)
        labels = assign_labels(distances)

        # 2) calcular sumas locales y conteos
        local_sums, local_counts = compute_local_sums(data, labels, k)

        # 3) reducir sumas y conteos globales
        global_sums = np.zeros_like(local_sums)
        global_counts = np.zeros_like(local_counts)
        comm.Allreduce(local_sums, global_sums, op=MPI.SUM)
        comm.Allreduce(local_counts, global_counts, op=MPI.SUM)

        # 4) rank 0 actualiza centroides
        if rank == 0:
            new_centroids = np.empty_like(centroids)
            for c in range(k):
                if global_counts[c] > 0:
                    new_centroids[c, :] = global_sums[c, :] / global_counts[c]
                else:
                    # cluster vacío: re-inicializar aleatoriamente (pequeño ruido)
                    # para evitar NaNs
                    new_centroids[c, :] = centroids[c, :]

            # calcular desplazamiento (norma del cambio total)
            shift = la.norm(new_centroids - centroids)
            centroids[:] = new_centroids
        else:
            shift = None

        # 5) broadcast del shift y de centroides actualizados 
        shift = comm.bcast(shift, root=0)
        comm.Bcast(centroids, root=0)

        if shift is not None and shift <= tol:
            if rank == 0:
                print(f"[rank 0] Converged at iter {it}, shift={shift:.6e}")
            break

    return centroids, labels


if __name__ == "__main__":
    # Parámetros configurables
    ntotal = 200000    # Número total de puntos
    d = 20              # Dimensión de los datos
    k = 3               # Número de clusters
    seed = 42           # Semilla para reproducibilidad 
    max_iters = 100     # Máximo de iteraciones
    tol =  1e-4         # Tolerancia para convergencia
    
    # Generar datos
    data = generate_distributed_data(ntotal, d, k, seed)
    
    # Ejecutar k-means
    comm.Barrier()
    t0 = MPI.Wtime()
    centroids, labels = kmeans_distributed(data, k, max_iters, tol)
    comm.Barrier()
    t1 = MPI.Wtime()

    # Para ir imprimiendo ciertas cosas:
    if rank == 0:
        print("Wall time:", t1 - t0)

        print("Centroids (rank 0):")
        print(centroids)
    print(f"rank {rank}: local n = {data.shape[0]}")