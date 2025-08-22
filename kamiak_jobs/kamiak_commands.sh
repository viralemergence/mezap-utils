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

# Download mammal phylogenetic tree
wget --no-check-certificate -O $DATA_DIR/Mammal_MCC.tre \
    https://github.com/n8upham/MamPhy_v1/raw/refs/heads/master/_DATA/MamPhy_fullPosterior_BDvr_Completed_5911sp_topoCons_NDexp_MCC_v2_target.tre

# Calculate phylogenetic distance matrix
singularity exec \
    --pwd /src \
    --no-home \
    --bind $APP_DIR:/src/app \
    --bind $DATA_DIR:/src/data \
    $SINGULARITY_IMAGE \
    python3 -u /src/app/phylogenetic_distance_calculator.py