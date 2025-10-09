#include <iostream>
#include <chrono>
#include <omp.h>
#include <fstream>
#include <vector>
#include <string>

bool is_prime(int n) {
    if (n < 2) return false;
    if (n == 2) return true;
    if (n % 2 == 0) return false;

    for (int i = 3; i * i <= n; i += 2) {
        if (n % i == 0) return false;
    }
    return true;
}

long long contar_primos(int limit, const std::string& mode, int threads, int chunk = 0) {
    long long count = 0;
    omp_set_num_threads(threads);

    auto start = std::chrono::high_resolution_clock::now();

    if (mode == "secuencial") {
        for (int n = 2; n < limit; n++) {
            if (is_prime(n)) count++;
        }
    } 
    else if (mode == "static") {
        if (chunk > 0) {
            #pragma omp parallel for reduction(+:count) schedule(static, chunk)
            for (int n = 2; n < limit; n++) {
                if (is_prime(n)) count++;
            }
        } else {
            #pragma omp parallel for reduction(+:count) schedule(static)
            for (int n = 2; n < limit; n++) {
                if (is_prime(n)) count++;
            }
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
        if (chunk > 0) {
            #pragma omp parallel for reduction(+:count) schedule(guided, chunk)
            for (int n = 2; n < limit; n++) {
                if (is_prime(n)) count++;
            }
        } else {
            #pragma omp parallel for reduction(+:count) schedule(guided)
            for (int n = 2; n < limit; n++) {
                if (is_prime(n)) count++;
            }
        }
    }

    auto end = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> duration = end - start;

    std::cout << "Modo: " << mode
              << " | Hilos: " << threads
              << " | Chunk: " << chunk
              << " | Tiempo: " << duration.count() << " s"
              << " | Primos: " << count << '\n';

    return count;
}

int main() {
    int limit = 400000000;  // Buscar primos hasta 400 millones
    std::vector<std::string> modes = {"secuencial", "static", "dynamic", "guided"};
    std::vector<int> threads_list = {2, 4, 8};
    std::vector<int> chunks = {0, 10, 1000, 10000};

    std::ofstream file("resultados.csv");
    file << "modo,threads,chunk,tiempo,primos\n";

    for (auto& mode : modes) {
        if (mode == "secuencial") {
            // Solo una corrida para la versión serial
            auto start = std::chrono::high_resolution_clock::now();
            long long count = contar_primos(limit, "secuencial", 1);
            auto end = std::chrono::high_resolution_clock::now();
            std::chrono::duration<double> duration = end - start;

            file << "secuencial,1,0," << duration.count() << "," << count << "\n";
        } else {
            // Para las demás estrategias, prueba distintas configuraciones
            for (auto& t : threads_list) {
                for (auto& chunk : chunks) {
                    auto start = std::chrono::high_resolution_clock::now();
                    long long count = contar_primos(limit, mode, t, chunk);
                    auto end = std::chrono::high_resolution_clock::now();
                    std::chrono::duration<double> duration = end - start;

                    file << mode << "," << t << "," << chunk << ","
                         << duration.count() << "," << count << "\n";
                }
            }
        }
    }

    file.close();
    std::cout << "\n✅ Resultados guardados en 'resultados.csv'\n";
    return 0;
}