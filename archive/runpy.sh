#!/bin/bash
#SBATCH --nodes=1
#SBATCH --cpus-per-task=12
#SBATCH --time=1:00:00
#SBATCH --mem=32GB
#SBATCH --job-name=iros
#SBATCH --output=iros_pm_%j.out

conda activate /scratch/ab9738/cctv_pollution/env/;
export PATH=/scratch/ab9738/cctv_pollution/env/bin:$PATH;
cd /scratch/ab9738/traffic/scalable-traffic-simulator/
python timelapse_images.py
