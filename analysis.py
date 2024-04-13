import re
from ciphers import analysis_ciphers
from dictionary import dictionary_all, AnagramLookupTable

# Transforms

def string_reverse(string: str) -> tuple[str, str]:
    return "".join(reversed(string)), "reverse"

def string_reverse_groups(string: str) -> tuple[str, str]:
    return " ".join([string_reverse(g)[0] for g in string.split(" ")]), "reverse groups"

def string_reverse_group_order(string: str) -> tuple[str, str]:
    return " ".join(reversed(string.split(" "))), "reverse group order"

def string_bigram_substitue(string: str) -> tuple[str, str]:
    if not " " in string and len(string) % 2 != 0:
        return None
    
    pairs = string.split(" ") if " " in string else [string[i:i+2] for i in range(0, len(string), 2)]
    
    result = ""
    substitutes_by_pair = {}
    next_char = 97
    for p in pairs:
        if p not in substitutes_by_pair:
            substitutes_by_pair[p] = chr(next_char)
            next_char += 1
        result += substitutes_by_pair[p]
    
    return result, "bigram group"


def apply_all_ciphers(string: str) -> list[tuple[str, str]]:
    results = []
    for cipher in analysis_ciphers:
        encoded = cipher.encode(string.encode("utf-8"))
        if isinstance(encoded, list):
           results += [(e, type(cipher).__name__) for e in encoded]
        elif encoded is not None:
            results.append((encoded, type(cipher).__name__))

        decoded = cipher.decode(string)
        if isinstance(decoded, list):
           results += [(d.decode("utf-8"), type(cipher).__name__) for d in decoded]
        elif decoded is not None:
            results.append((decoded.decode("utf-8"), type(cipher).__name__))

    return results

analysis_anagram_lookup_table = AnagramLookupTable(dictionary_all)
def apply_anagram_search(string: str) -> list[tuple[str, str]]:
    anagrams = analysis_anagram_lookup_table.lookup(string)
    return [(a, "anagram") for a in anagrams] if anagrams is not None else []

# not yet implemented: guess substitution cypher


transforms = [string_reverse, string_reverse_group_order, string_reverse_groups, apply_all_ciphers, apply_anagram_search]


# Validators

def is_isbn(string: str, dictionary: list[str]) -> bool:
    d = [int(c) if c.isdigit() else 10 for c in string.lower() if c.isdigit() or c == "x"]
    if len(d) == 10:
        d = [9, 8, 7] + d  # prepend 987 to convert to 13-digit ISBN
    if len(d) != 13:
        return False
    checksum = (1 * d[0] + 3 * d[1] + 1 * d[2] + 3 * d[3] + 1 * d[4] + 3 * d[5] + 1 * d[6] + 3 * d[7] + 1 * d[8] + 3 * d[9] + 1 * d[10] + 3 * d[11] + 1 * d[12]) % 10
    return checksum == 0


def is_part_word(string: str, dictionary: list[str]) -> bool:
    words = []
    special_chars = ["-", ":", ".", ",", ";", "_", ]
    if " " in string:
        words += [re.sub(r"[^a-z]", "", w.lower()) for w in string.split(" ")]
    if any([it in string for it in special_chars]):
        words += [re.sub(r"[^a-z]", "", w.lower()) for w in re.sub(r"[\-:\.,;_]", " ", string).split(" ")]
    
    if len(words) == 0:
        words.append(string)
    
    return any([word in dictionary for word in words if len(word) >= 3])

def is_german_phone_number(string: str, dictionary: list[str]) -> bool:
    return re.sub(r"\D", "", string).startswith("49")

def could_be_coordinate(string: str, dictionary: list[str]) -> bool:
    return (any([it in string for it in ["N", "S"]]) and any([it in string for it in ["E", "W"]])) and any([it.isdigit() for it in string])

validators = [is_part_word, is_isbn, is_german_phone_number, could_be_coordinate]




# Bruteforce analysis
class BruteforceResult:
    string: str
    path: list[str]
    depth: int
    validator: str

    def __init__(self, string: str, path: list[str], depth: int):
        self.string = string
        self.path = path
        self.depth = depth
        self.validator = None
    
    def __str__(self) -> str:
        return f"{self.string}      ---   {"->".join(self.path)}   ---   {self.validator.__name__}"


def bruteforce_string(string: str, path: list[str] = [], total_iterations: int = 3, depth: int = 0, seen_already: set[str] = set()) -> set[BruteforceResult]:
    if depth == total_iterations:
        return set()
    
    string = string.lower()
    
    results = set()

    for transform in transforms:
        # generate candidates
        new_candidates = transform(string)
        if isinstance(new_candidates, list):
            new_results = [BruteforceResult(c[0], path + [c[1]], depth + 1) for c in set(new_candidates)]
        else:
            new_results = [BruteforceResult(new_candidates[0], path + [new_candidates[1]], depth + 1)]

        # filter already seen, long, unknown, non alphanumerical
        new_results = [r for r in new_results if not r.string in seen_already]
        new_results = [r for r in new_results if len(r.string) < 200 and r.string.count("?") < 5]
        new_results = [r for r in new_results if any([c.isalnum() for c in r.string])]
        
        # for r in new_results:
        #     print(r.string)

        
        # todo move deepen and validation out of transform iteration?

        # deepen
        seen_already = seen_already.union(set([r.string for r in new_results]))  # previous deeper iterations are now unseen, could be returned and passed around
        new_results += [ cr for r in new_results for cr in bruteforce_string(r.string, r.path, total_iterations, depth + 1, seen_already) ]  # list comprehensions are magic

        # add results
        results = results.union(set(new_results))
    
    # validate
    for r in results:
        for v in validators:
            if v(r.string, dictionary_all):
                r.validator = v
                break
    
    results = set([r for r in results if r.validator is not None])

    return results
    


# Test
if __name__ == "__main__":
    results = bruteforce_string("3 22 4 9 99 55 9999 8 55 6 99 4", total_iterations=4)
    results_filtered = []
    for r in sorted(results, key=lambda r: r.depth):
        if not r.string in [it.string for it in results_filtered]:
            results_filtered.append(r)
    results_filtered = list(sorted(results_filtered, key=lambda r: validators.index(r.validator)))

    for r in results_filtered:
        print(r)

