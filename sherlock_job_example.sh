#!/bin/bash

#SBATCH --job-name=auto_ml
#SBATCH --time=4:30:00
#SBATCH --mem=10GB
#SBATCH --partition=hns
#SBATCH --chdir=/home/users/sofiaaj/noxiousness/physical_area
#SBATCH --mail-type=ALL
#SBATCH --output=job_output_automl_phys_area.out
#SBATCH --error=job_output_automl_phys_area.err

 ml R/3.5.1
 srun Rscript run_automl.R