from argparse import ArgumentParser
from csv import DictReader
from pathlib import Path
from shutil import move, rmtree
import subprocess
from typing import Union
import zipfile

class TaxaInfoParser:
    def __init__(self, taxa_info_path: Path, column_of_interest: str):
        self.taxa_info = self.extract_taxa_info(taxa_info_path, column_of_interest)

    @staticmethod
    def extract_taxa_info(taxa_info_path: Path, column_of_interest: str) -> list[str]:
        with taxa_info_path.open() as inhandle:
            return [data[column_of_interest] for data in DictReader(inhandle)]

class DatasetsManager:
    def __init__(self, outdir: Path):
        self.outdir = outdir

    def run(self, taxon_uid: str, failed_taxa_path: Path) -> None:
        if (zip_file_path := self.download_cds_for_taxon_uid(taxon_uid, self.outdir, failed_taxa_path)) is None:
            return

        unzipped_dir = self.outdir / f"{taxon_uid.replace(' ', '_')}"
        self.unzip_file(zip_file_path, unzipped_dir)
        zip_file_path.unlink()

        if (cds_path := self.extract_cds_path(unzipped_dir)) is None:
            rmtree(unzipped_dir)
            return

        new_cds_path = self.outdir / f"{taxon_uid.replace(' ', '_')}_cds.fna"
        move(cds_path, new_cds_path)
        rmtree(unzipped_dir)

    @staticmethod
    def download_cds_for_taxon_uid(taxon_uid: str, outdir: Path,
                                   failed_taxa_path: Path) -> Union[Path, None]:
        zip_file_path = outdir / f"{taxon_uid.replace(' ', '_')}_datasets.zip"

        datasets_command = ["datasets", "download", "genome", "taxon", f"{taxon_uid}",
                            "--include", "cds", "--assembly-source", "RefSeq",
                            "--assembly-version", "latest",
                            "--filename", f"{zip_file_path}"]

        p = subprocess.Popen(datasets_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        while p.poll() is None and (line := p.stderr.readline()) != "":
            print(line.strip())
        p.wait()

        if p.poll() != 0:
            print(f"Datasets submission for {taxon_uid} did not complete successfully")
            with failed_taxa_path.open("a") as outhandle:
                outhandle.write(f"{taxon_uid}\n")
            return None
        return zip_file_path

    @staticmethod
    def unzip_file(zip_file_path: Path, outdir: Path) -> None:
        with zipfile.ZipFile(zip_file_path, "r") as zip_handle:
            zip_handle.extractall(outdir)

    @staticmethod
    def extract_cds_path(unzipped_dir: Path) -> Union[Path, None]:
        cds_parent_dir = unzipped_dir / "ncbi_dataset" / "data"
        cds_dir = None
        for path in cds_parent_dir.iterdir():
            if path.is_dir():
                cds_dir = path
                break
        if cds_dir is None:
            return
        cds_path = cds_dir / "cds_from_genomic.fna"
        return cds_path

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-taxa_info", type=str, required=True)
    parser.add_argument("-column_of_interest", type=str, default="taxon_genus_species")
    parser.add_argument("-outdir", type=str, required=True)
    parser.add_argument("-failed_taxa", type=str, required=True)
    args = parser.parse_args()

    tip = TaxaInfoParser(Path(args.taxa_info), args.column_of_interest)

    dm = DatasetsManager(Path(args.outdir))
    for taxon_uid in tip.taxa_info:
        print(f"Starting on: {taxon_uid}")
        dm.run(taxon_uid, Path(args.failed_taxa))