import time
from numba import njit, prange, set_num_threads, get_num_threads

@njit 
def is_prime(n):
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    i = 3
    while i * i <= n:
        if n % i == 0:
            return False
        i += 2
    return True

@njit
def count_primes_sequential(limit):
    count = 0
    for num in range(2, limit):
        if is_prime(num):
            count += 1
    return count

@njit(parallel=True)
def count_primes_parallel(limit):
    count = 0
    for num in prange(2, limit):
        if is_prime(num):
            count += 1
    return count


if __name__ == "__main__":
    set_num_threads(4)  # numero de hilos
    print(f"Usando {get_num_threads()} threads")
    print()
    
    limit = 400000000  
    
    # Versión secuencial con Numba
    print("=== Versión Secuencial con Numba ===")
    start = time.time()
    count = count_primes_sequential(limit)
    end = time.time()
    
    print(f"Rango: 2 a {limit}")
    print(f"Primos encontrados: {count}")
    print(f"Tiempo: {end - start:.2f} segundos")
    print()
    
    # Versión paralela con Numba
    print("=== Versión Paralela con Numba ===")
    start = time.time()
    count = count_primes_parallel(limit)
    end = time.time()
    
    print(f"Rango: 2 a {limit}")
    print(f"Primos encontrados: {count}")
    print(f"Tiempo: {end - start:.2f} segundos")