#!/bin/bash
#SBATCH --job-name=kmeans_mpi
#SBATCH --partition=hpc-iic3533
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=4
#SBATCH --cpus-per-task=2
#SBATCH --time=00:15:00
#SBATCH --output=kmeans_%j.out
#SBATCH --chdir=/home/pleiva/kmeans

echo "Job ID: $SLURM_JOBID"
echo "Nodos: $SLURM_JOB_NODELIST"
echo "NTASKS = $SLURM_NTASKS  CPUS_PER_TASK = $SLURM_CPUS_PER_TASK"

# Activar entorno conda
source ~/miniconda3/bin/activate kmeans_env

# Configurar threads Numba
export NUMBA_NUM_THREADS=$SLURM_CPUS_PER_TASK

# Ejecutar
mpirun -n $SLURM_NTASKS python distributed.py
