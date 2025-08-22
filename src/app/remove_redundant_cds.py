from argparse import ArgumentParser
from collections import defaultdict
from pathlib import Path
from typing import Iterator

class CdsManager:
    def __init__(self, cds_dir_path: Path, outdir_path: Path, header_type: int) -> None:
        self.cds_dir_path = cds_dir_path
        self.cds_paths = self.extract_cds_paths(self.cds_dir_path)

        self.outdir_path = outdir_path
        self.header_type = header_type

    @staticmethod
    def extract_cds_paths(cds_dir_path: Path) -> list[Path]:
        return [file for file in cds_dir_path.iterdir() if file.is_file()]

    def run(self, cds_path: Path) -> None:
        print(f"Starting on: {cds_path.stem}")
        unique_ids = self.extract_ids_for_non_redundant_sequences(cds_path, self.header_type)

        outpath = self.outdir_path / f"{cds_path.stem.replace('_cds', '_nonredundant_cds')}.fna"
        with outpath.open("w") as outhandle:
            for fasta_feature in self.fasta_chunker(cds_path):
                fasta_name = fasta_feature[0]
                if fasta_name not in unique_ids:
                    continue
                for line in fasta_feature:
                    outhandle.write(f"{line}\n")

    @classmethod
    def extract_ids_for_non_redundant_sequences(cls, fasta_path: Path, header_type: int) -> set[str]:
        sequence_info = defaultdict(lambda: defaultdict(int))
        for fasta_feature in cls.fasta_chunker(fasta_path):
            fasta_name = fasta_feature[0]
            if header_type == 0:
                # >lcl|NC_014373.1_cds_YP_003815432.1_1 [gene=NP] [locus_tag=BDBVp1] [db_xref=GeneID:9487269] [protein=nucleoprotein] [protein_id=YP_003815432.1] [location=458..2677] [gbkey=CDS]
                gene = fasta_name.split("[")[1].strip().replace("gene=", "")[:-1] # NOTE: Should clean up
            if header_type == 1:
                # >NC_055939.1:85..3213 |glycoprotein [Scaldis River bee virus]
                gene = fasta_name.split("|")[1].split("[")[0].strip()
            fasta_seq_len = len("".join(fasta_feature[1:]))

            lead_seq_length = sequence_info[gene]["length"]
            if fasta_seq_len > lead_seq_length:
                sequence_info[gene]["length"] = fasta_seq_len
                sequence_info[gene]["id"] = fasta_name

        ids_for_non_redundant_sequences = set()
        for gene, info in sequence_info.items():
            unique_id = info["id"]
            ids_for_non_redundant_sequences.add(unique_id)

        return ids_for_non_redundant_sequences

    @staticmethod
    def fasta_chunker(fasta_path: Path) -> Iterator[list[str]]:
        fasta_seq = []
        first_chunk = True
        with fasta_path.open() as inhandle:
            for line in inhandle:
                line = line.strip()
                if not line.startswith(">"):
                    fasta_seq.append(line)
                else:
                    if first_chunk:
                        fasta_seq.append(line)
                        first_chunk = False
                        continue
                    yield fasta_seq
                    fasta_seq = [line]
            if fasta_seq:
                yield fasta_seq

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-cds_dir", type=str, required=True)
    parser.add_argument("-outdir", type=str, required=True)
    parser.add_argument("-header", type=int, required=True)
    args = parser.parse_args()

    cm = CdsManager(Path(args.cds_dir), Path(args.outdir), args.header)
    for cds_path in cm.cds_paths:
        cm.run(cds_path)