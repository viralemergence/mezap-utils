FROM ubuntu:22.04

WORKDIR /src

RUN apt-get update \
    && apt-get install -y wget \
    && apt install make \
    && apt install python3 -y

# Install NCBI Datasets
RUN wget https://ftp.ncbi.nlm.nih.gov/pub/datasets/command-line/v2/linux-amd64/datasets -P /src/tools/datasets

# Configure Datasets
ENV PATH="/src/tools/datasets:$PATH"
RUN chmod +x /src/tools/datasets/datasets

# Install biopython for phylogenetic distance calculations
RUN apt-get update \
    && apt install python3-pip -y \
    && pip install biopython