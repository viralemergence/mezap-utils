from argparse import ArgumentParser
from Bio import Phylo # type: ignore
from pathlib import Path

class QuerySpeciesManager:
    def __init__(self, query_species_dir: Path) -> None:
        self.query_species = self.extract_species_names(query_species_dir)

    @staticmethod
    def extract_species_names(query_species_dir: Path) -> list[str]:
        query_species = []
        for file in query_species_dir.iterdir():
            if not file.is_file():
                continue
            file_name = file.stem
            name_elements = file_name.split("_")
            genus_species = " ".join(name_elements[0:-2]).capitalize()
            query_species.append(genus_species)
        return query_species

class PhylogeneticTreeManager:
    def __init__(self, tree_path: Path) -> None:
        print("Loading tree")
        self.tree = Phylo.read(tree_path, "nexus")

    def rename_tips(self) -> None:
        tips = self.tree.get_terminals()
        for tip in tips:
            tip_name = tip.name.replace("_", " ").strip()
            simplified_name = " ".join([word for word in tip_name.split(" ") if not word.isupper()])
            tip.name = simplified_name

    def prune_tree(self, query_species: list[str]) -> None:
        print("Pruning tree")
        extra_tips = []
        tips = self.tree.get_terminals()
        for tip in tips:
            if tip.name not in query_species:
                extra_tips.append(tip)

        for tip in extra_tips:
            self.tree.prune(tip)
        tips = self.tree.get_terminals()

    def calculate_distance_matrix(self) -> list[list[float]]:
        print("Calculating distance matrix")
        tips = self.tree.get_terminals()

        distance_matrix = []
        for i in range(len(tips)):
            if i % 50 == 0:
                print(f"Starting on tip: {i}")
            row = []
            for j in range(len(tips)):
                tip_1 = tips[i]
                tip_2 = tips[j]
                distance = self.tree.distance(tip_1, tip_2)
                row.append(distance)
            distance_matrix.append(row)
        return distance_matrix

    def write_distance_matrix(self, distance_matrix_outpath: Path,
                              distance_matrix: list[list[float]]) -> None:
        print("Writing distance matrix")
        tips = self.tree.get_terminals()

        header = [""] + [tip.name for tip in tips]
        with distance_matrix_outpath.open("w") as outhandle:
            outhandle.write(f"{','.join(header)}\n")
            for i, row in enumerate(distance_matrix, 1):
                out_line = [header[i]] + [str(dist) for dist in row]
                outhandle.write(f"{','.join(out_line)}\n")

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-query_species_dir", type=str, required=True)
    parser.add_argument("-phylo_tree", type=str, required=True)
    parser.add_argument("-distance_matrix", type=str, required=True)
    args = parser.parse_args()

    qsm = QuerySpeciesManager(Path(args.query_species_dir))
    
    ptm = PhylogeneticTreeManager(Path(args.phylo_tree))
    ptm.rename_tips()
    ptm.prune_tree(qsm.query_species)

    distance_matrix = ptm.calculate_distance_matrix()
    ptm.write_distance_matrix(Path(args.distance_matrix), distance_matrix)