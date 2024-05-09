# https://oeis.org/stripped.gz

class OeisDatabase:
    entries: dict[str, str] # comma separated for searchability

    def __init__(self, filename: str) -> None:
        self.entries = {}

        print("Building OEIS database...")
        with open(filename, 'r') as f:
            lines = f.readlines()
            lines = [line for line in lines if not line.startswith('#') and len(line) > 0]
            for line in lines:
                id, seq = line.split(",", maxsplit=1)
                self.entries[id.strip()] = seq.strip()[:-1]
        print(f"OEIS database built, {len(self.entries)} entries.")
    
    def lookup_by_index(self, index: str) -> str | None:
        index = index.strip()
        if not index.startswith("A"):
            index = "A" + index
        return self.entries.get(index, None)

    def lookup_by_sequence(self, seq: str) -> list[tuple[str, str]]:
        return [(id, s) for id, s in self.entries.items() if seq.strip().replace(" ", ",") in s]
    
oeis_database = OeisDatabase("oeis.txt")
    
