from argparse import ArgumentParser
from csv import DictReader
from pathlib import Path
from shutil import move, rmtree
import subprocess
import zipfile

class TaxonIdParser:
    def __init__(self, taxon_ids_path: Path):
        self.taxon_ids = self.extract_taxon_ids(taxon_ids_path)

    @staticmethod
    def extract_taxon_ids(taxon_ids_path: Path) -> list[int]:
        with taxon_ids_path.open() as inhandle:
            return [int(data["taxon_id"]) for data in DictReader(inhandle)]

class DatasetsManager:
    def __init__(self, outdir: Path):
        self.outdir = outdir

    def run(self, taxon_id: int) -> None:
        zip_file_path = self.download_cds_for_taxon_id(taxon_id, self.outdir)

        unzipped_dir = self.outdir / f"{taxon_id}"
        self.unzip_file(zip_file_path, unzipped_dir)
        zip_file_path.unlink()

        cds_path = self.extract_cds_path(unzipped_dir)
        new_cds_path = self.outdir / f"{taxon_id}_cds.fna"
        move(cds_path, new_cds_path)
        rmtree(unzipped_dir)

    @staticmethod
    def download_cds_for_taxon_id(taxon_id: int, outdir: Path) -> Path:
        zip_file_path = outdir / f"{taxon_id}_datasets.zip"

        datasets_command = ["datasets", "download", "genome", "taxon", f"{taxon_id}",
                            "--include", "cds", "--assembly-source", "RefSeq",
                            "--assembly-version", "latest",
                            "--filename", f"{zip_file_path}"]

        p = subprocess.Popen(datasets_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        while p.poll() is None and (line := p.stderr.readline()) != "":
            pass
            # print(line.strip())
        p.wait()

        if p.poll() != 0:
            print(p.stderr.readlines())
            raise Exception("Datasets submission did not complete successfully")
        return zip_file_path

    @staticmethod
    def unzip_file(zip_file_path: Path, outdir: Path) -> None:
        with zipfile.ZipFile(zip_file_path, "r") as zip_handle:
            zip_handle.extractall(outdir)

    @staticmethod
    def extract_cds_path(unzipped_dir: Path) -> Path:
        cds_parent_dir = unzipped_dir / "ncbi_dataset" / "data"
        for path in cds_parent_dir.iterdir():
            if path.is_dir():
                cds_dir = path
                break
        cds_path = cds_dir / "cds_from_genomic.fna"
        return cds_path

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-taxon_ids", type=str, required=True)
    parser.add_argument("-outdir", type=str, required=True)
    args = parser.parse_args()

    tip = TaxonIdParser(Path(args.taxon_ids))

    dm = DatasetsManager(Path(args.outdir))
    for taxon_id in tip.taxon_ids:
        print(f"Starting on: {taxon_id}")
        dm.run(taxon_id)