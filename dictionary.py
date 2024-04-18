import re


with open("words_sorted.txt") as f:
    dictionary_all = [l.replace("\n", "") for l in f.readlines()]

with open("words_popular.txt") as f:
    dictionary_popular = [l.replace("\n", "") for l in f.readlines()]

class AnagramLookupTable:
    table: dict[str, list[str]]

    def __init__(self, dictionary: list[str]) -> None:
        print(f"Building anagram lookup table for {len(dictionary)} words...")
        self.build_table(dictionary)
        print(f"Lookup table built, {len(self.table)} entries")

    def build_table(self, dictionary: list[str]):
        self.table = {}

        for word in dictionary:
            word_sorted = self.sort_word(word)

            if not word_sorted in self.table:
                self.table[word_sorted] = []
            
            self.table[word_sorted].append(word)
    
    def sort_word(self, word: str) -> str:
        return "".join(sorted(word))

    def lookup(self, word: str) -> list[str] | None:
        word = word.lower()
        if "?" in word:
            results = []
            for c in [chr(i + 97) for i in range(26)]:
                discovered = self.lookup(word.replace("?", c, 1))
                if discovered is not None:
                    results += discovered
            return list(set(results)) if len(results) != 0 else None

        sorted_word = self.sort_word(word)
        if sorted_word in self.table:
            return self.table[self.sort_word(word)]
        else:
            return None


def find_words_by_regex(regex: re.Pattern, dictionary: list[str]) -> list[str]:
    return [word for word in dictionary if regex.fullmatch(word)]