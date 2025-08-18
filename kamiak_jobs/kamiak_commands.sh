# Download Docker image to Kamiak with Singularity and convert to Singularity image
mkdir ./src/singularity_image
module load singularity
singularity pull ./src/singularity_image/mu.sif docker://ghcr.io/viralemergence/mezap-utils:latest

# For making scratch space
mkworkspace
export myscratch="$(mkworkspace)"
echo $myscratch
lsworkspace

# Down CDS by taxon id
mkdir $DATASETS_DIR
singularity exec \
    --pwd /src \
    --no-home \
    --bind /etc:/etc \
    --env NCBI_API_KEY=$NCBI_API_KEY \
    --bind $APP_DIR:/src/app \
    --bind $DATA_DIR:/src/data \
    --bind $DATASETS_DIR:/src/datasets \
    $SINGULARITY_IMAGE \
    python3 -u /src/app/cds_download.py \
    -taxon_ids /src/data/taxon_ids.csv \
    -outdir /src/datasets