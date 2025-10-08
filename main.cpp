#include <iostream>
#include <chrono>
#include <vector>
#include <omp.h>

bool is_prime(int n) {
    if (n < 2) return false;
    if (n == 2) return true;
    if (n % 2 == 0) return false;

    for (int i = 3; i * i <= n; i += 2) {
        if (n % i == 0) return false;
    }
    return true;
}

long long contar_primos(int limit, const std::string& mode, int chunk = 0) {
    long long count = 0;

    auto start = std::chrono::high_resolution_clock::now();

    if (mode == "secuencial") {
        for (int n = 2; n < limit; n++) {
            if (is_prime(n)) count++;
        }
    }
    else if (mode == "static") {
        #pragma omp parallel for reduction(+:count) schedule(static)
        for (int n = 2; n < limit; n++) {
            if (is_prime(n)) count++;
        }
    }
    else if (mode == "dynamic") {
        if (chunk > 0) {
            #pragma omp parallel for reduction(+:count) schedule(dynamic, chunk)
            for (int n = 2; n < limit; n++) {
                if (is_prime(n)) count++;
            }
        } else {
            #pragma omp parallel for reduction(+:count) schedule(dynamic)
            for (int n = 2; n < limit; n++) {
                if (is_prime(n)) count++;
            }
        }
    }
    else if (mode == "guided") {
        #pragma omp parallel for reduction(+:count) schedule(guided)
        for (int n = 2; n < limit; n++) {
            if (is_prime(n)) count++;
        }
    }

    auto end = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> duration = end - start;

    std::cout << "=== " << mode << " ===" << std::endl;
    std::cout << "Rango: 2 a " << limit << std::endl;
    std::cout << "Primos encontrados: " << count << std::endl;
    std::cout << "Tiempo: " << duration.count() << " segundos" << std::endl;
    std::cout << "Hilos usados: " << omp_get_max_threads() << "\n\n";

    return count;
}

int main() {
    int limit = 400000000;  // Buscar primos hasta 400 millones
    omp_set_num_threads(16);

    std::cout << "===== PRUEBAS DE OPENMP =====\n";
    std::cout << "Procesadores disponibles: " << omp_get_num_procs() << "\n";
    std::cout << "Máx. hilos: " << omp_get_max_threads() << "\n\n";

    contar_primos(limit, "secuencial");
    contar_primos(limit, "static");
    contar_primos(limit, "dynamic");
    contar_primos(limit, "guided");
    contar_primos(limit, "dynamic", 1000); 

    return 0;
}
