#!/bin/bash
#SBATCH --partition=remi
#SBATCH --job-name=host_cds_download
#SBATCH --output=%x_%j.out
#SBATCH --error=%x_%j.err
#SBATCH --mail-type=ALL
#SBATCH --mail-user=alexander.brown@wsu.edu
#SBATCH --time=3-00:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=20G

ENV_FILE=$1
. $ENV_FILE

mkdir $DATASETS_DIR/hosts

module load singularity

# Download host CDS by taxon name
singularity exec \
    --pwd /src \
    --no-home \
    --bind /etc:/etc \
    --env NCBI_API_KEY=$NCBI_API_KEY \
    --bind $APP_DIR:/src/app \
    --bind $DATA_DIR:/src/data \
    --bind $DATASETS_DIR/hosts:/src/datasets \
    $SINGULARITY_IMAGE \
    python3 -u /src/app/cds_download.py \
    -taxa_info /src/data/unique_hosts.csv \
    -outdir /src/datasets \
    -failed_taxa /src/data/failed_host_taxa_cds_download.txt