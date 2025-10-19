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
    limit = 400000000
    threads_list = [1, 2, 4, 6, 8, 10, 12]
    
    # Crear archivo CSV para resultados
    with open('resultados_numba.csv', 'w') as f:
        f.write('modo,threads,chunk,tiempo,primos\n')
        # Versión secuencial
        print("=== Versión Secuencial con Numba ===")
        start = time.time()
        count = count_primes_sequential(limit)
        end = time.time()
        duration = end - start
        
        print(f"Modo: secuencial | Threads: 1 | Tiempo: {duration:.2f} s | Primos: {count}")
        f.write(f'secuencial,1,NA,{duration},{count}\n')
        print()
        
        # Versión paralela con diferentes números de threads
        print("=== Versión Paralela con Numba ===")
        for threads in threads_list:
            set_num_threads(threads)
            
            start = time.time()
            count = count_primes_parallel(limit)
            end = time.time()
            duration = end - start
            
            print(f"Modo: paralelo | Threads: {threads} | Tiempo: {duration:.2f} s | Primos: {count}")
            f.write(f'paralelo,{threads},NA,{duration},{count}\n')
    
    print("\nResultados guardados en 'resultados_numba.csv'")