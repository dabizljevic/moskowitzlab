#!/bin/bash
#SBATCH --job-name=nfcore_bulk_rnaseq_run_240625
#SBATCH -n 1
#SBATCH -N 4
#SBATCH -t 24:00:00
#SBATCH --mem-per-cpu=64gb 
#SBATCH --mail-user=root@uchicago.edu
#SBATCH --mail-type=end
#SBATCH --account=pi-imoskowitz
#SBATCH --partition=caslake
module load python/anaconda-2022.05
source activate /project/imoskowitz/shared/software/nf-core
module load singularity

export TMPDIR="/scratch/midway3/root"

export NXF_TEMP="/scratch/midway3/root"

export NXF_SINGULARITY_CACHEDIR="/project/imoskowitz/shared/software/singularityImages" 
nextflow run \
/project/imoskowitz/shared/software/nf-core-rnaseq_3.13.2/3_13_2/ -work-dir /scratch/midway3/root/working_20240615_LH00315_0209_A22KFLMLT3-IM-SAB-RS72 \
-profile singularity -params-file /Users/sdabiz/Desktop/work/2024summer/moskowitzlab/sequencing/output/20240615_LH00315_0209_A22KFLMLT3-IM-SAB-RS72/rnaseq_params.yaml -c /project/imoskowitz/shared/software/assets/test3.config 
