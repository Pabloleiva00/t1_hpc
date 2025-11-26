#!/bin/bash
#SBATCH --job-name=kmeans_mpi
#SBATCH --partition=hpc-iic3533
#SBATCH --mem=3900mb
#SBATCH --time=00:15:00
#SBATCH --output=kmeans_%j.out
#SBATCH --chdir=/home/pleiva/kmeans

# Activar entorno conda
source ~/miniconda3/bin/activate kmeans_env

# Configurar threads Numba
export NUMBA_NUM_THREADS=$SLURM_CPUS_PER_TASK

# Ejecutar
mpirun -n $SLURM_NTASKS python distributed.py