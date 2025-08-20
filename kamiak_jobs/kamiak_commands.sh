# Download Docker image to Kamiak with Singularity and convert to Singularity image
mkdir ./src/singularity_image
module load singularity
singularity pull ./src/singularity_image/mu.sif docker://ghcr.io/viralemergence/mezap-utils:latest

# For making scratch space
mkworkspace
export myscratch="$(mkworkspace)"
echo $myscratch
lsworkspace

mkdir $DATASETS_DIR

# Download host CDS by taxon name
mkdir $DATASETS_DIR/hosts
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

# Download virus CDS by taxon name
mkdir $DATASETS_DIR/viruses
singularity exec \
    --pwd /src \
    --no-home \
    --bind /etc:/etc \
    --env NCBI_API_KEY=$NCBI_API_KEY \
    --bind $APP_DIR:/src/app \
    --bind $DATA_DIR:/src/data \
    --bind $DATASETS_DIR/viruses:/src/datasets \
    $SINGULARITY_IMAGE \
    python3 -u /src/app/cds_download.py \
    -taxa_info /src/data/unique_viruses.csv \
    -outdir /src/datasets \
    -failed_taxa /src/data/failed_virus_taxa_cds_download.txt

mkdir $CDS_DIR

# Remove redundant CDS for hosts
mkdir $CDS_DIR/hosts
singularity exec \
    --pwd /src \
    --no-home \
    --bind $APP_DIR:/src/app \
    --bind $DATASETS_DIR:/src/datasets \
    --bind $CDS_DIR/hosts:/src/cds \
    $SINGULARITY_IMAGE \
    python3 -u /src/app/remove_redundant_cds.py \
    -cds_dir /src/datasets/hosts \
    -outdir /src/cds -header 0

# Remove redundant CDS for viruses
mkdir $CDS_DIR/viruses
singularity exec \
    --pwd /src \
    --no-home \
    --bind $APP_DIR:/src/app \
    --bind $DATASETS_DIR:/src/datasets \
    --bind $CDS_DIR/viruses:/src/cds \
    $SINGULARITY_IMAGE \
    python3 -u /src/app/remove_redundant_cds.py \
    -cds_dir /src/datasets/viruses \
    -outdir /src/cds -header 0