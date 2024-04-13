import re


# Validators

def is_isbn(string: str) -> bool:
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

def is_german_phone_number(string: str) -> bool:
    return re.sub(r"\D", "", string).startswith("49")

def could_be_coordinate(string: str) -> bool:
    return (any([it in string for it in ["N", "S"]]) and any([it in string for it in ["E", "W"]])) and any([it.isdigit() for it in string])

