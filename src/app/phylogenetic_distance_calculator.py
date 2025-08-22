from argparse import ArgumentParser
from Bio import Phylo
from pathlib import Path
from typing import Union

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-column_of_interest", type=str, default="taxon_genus_species")
    args = parser.parse_args()

    pass