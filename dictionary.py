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


from typing import Self

class T9LookupTree:

    class T9TreeNode:
        children: list[Self | None]
        words: list[str]

        def __init__(self) -> None:
            self.children = [None for _ in range(10)]
            self.words = []
    
    root: T9TreeNode
    key_lookup: dict[str, int]

    def __init__(self, dictionary: list[str]) -> None:
        self.root = self.T9TreeNode()
        self.key_lookup = {
            "a": 2,
            "b": 2,
            "c": 2,
            "d": 3,
            "e": 3,
            "f": 3,
            "g": 4,
            "h": 4,
            "i": 4,
            "j": 5,
            "k": 5,
            "l": 5,
            "m": 6,
            "n": 6,
            "o": 6,
            "p": 7,
            "q": 7,
            "r": 7,
            "s": 7,
            "t": 8,
            "u": 8,
            "v": 8,
            "w": 9,
            "x": 9,
            "y": 9,
            "z": 9,
            "+": 0,
        }

        print(f"Building T9 lookup tree for {len(dictionary)} words...")
        self.build_tree(dictionary)
        print(f"Lookup tree built")


    def build_tree(self, dictionary: list[str]):
        for word in dictionary:
            current = self.root
            for c in word:
                n = self.key_lookup[c.lower()] - 1
                if current.children[n] is None:
                    current.children[n] = self.T9TreeNode()
                current = current.children[n]

            current.words.append(word)
    
    def lookup(self, input: str, multipart: bool = False) -> str:
        if " " in input:
            return " ".join([self.lookup(s, multipart=True) for s in input.split(" ")])
        if any([not c.isdigit() for c in input]):
            return "Ahoy matey! We cannot sail the high seas of the lookup tree with that input."
        
        current = self.root
        for c in input:
            current = current.children[int(c) - 1]
            if current is None:
                return "No match found"
        
        if multipart:
            return str(current.words)
        else:
            return "\n".join(current.words)

