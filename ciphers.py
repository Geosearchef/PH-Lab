from dictionary import dictionary_all, dictionary_popular, T9LookupTree

class Cipher:
    def __init__(self, name) -> None:
        self.name = name

    def encode(self, data: bytes, key: str | None = None) -> str:
        return data.decode("utf-8")
    
    def decode(self, string: str, key: str | None = None) -> bytes:
        return string.encode("utf-8")

class TextCipher(Cipher):
    def __init__(self) -> None:
        super().__init__("Text")

    def encode(self, data: bytes, key: str | None = None) -> str:
        return data.decode("utf-8")
    
    def decode(self, string: str, key: str | None = None) -> bytes:
        return string.encode("utf-8")

class HexAsciiCipher(Cipher):
    def __init__(self) -> None:
        super().__init__("Hex")

    def encode(self, data: bytes, key: str | None = None) -> str:
        string = data.decode("utf-8")
        out = " ".join([str(hex(ord(c))[2:]) for c in string])
        return out
    
    def decode(self, string: str, key: str | None = None) -> bytes:
        string = string.replace("0x", "")

        if not " " in string and len(string) % 2 != 0:
           return "No spaces in string and string of odd length".encode("utf-8")
        
        char_vals = string.split(" ") if " " in string else [string[i:i+2] for i in range(0, len(string), 2)]
        try: 
            chars = [chr(int(h, 16)) for h in char_vals if h != ""]
        except ValueError:
            return "Please use valid hexadecimal values".encode("utf-8")

        return ("".join(chars)).encode("utf-8")


class NumbersCipher(Cipher):
    def __init__(self) -> None:
        super().__init__("Numbers")

    def encode(self, data: bytes, key: str | None = None) -> str:
        string = data.decode("utf-8")
        out = " ".join([str(ord(c) % 32) for c in string if c.isalpha()]) # todo: auto split with even length
        return out
    
    def decode(self, string: str, key: str | None = None) -> bytes:
        if not " " in string and len(string) % 2 != 0:
           return "No spaces in string and string of odd length".encode("utf-8")
        
        number_strings = string.split() if " " in string else [string[i:i+2] for i in range(0, len(string), 2)]
        
        try:
            out = "".join([chr(int(n) % 32 + 96) for n in number_strings])
        except ValueError:
            out = ""
        
        return out.encode("utf-8")


class CaesarCipher(Cipher):
    def __init__(self) -> None:
        super().__init__("Caesar")

    def shift_char(self, c, shift):
        if not c.isalpha():
            return c
        
        n = ord(c) % 32
        sn = (n + shift - 1 + 26) % 26 + 1  # +26 to deal with negative keys, removed by remainder op again
        return chr(sn + 96)


    def encode(self, data: bytes, key: str | None = "all") -> str | list[str]:
        if key is None or not key.isnumeric():
            return [str(self.encode(data, key=str(shift))) for shift in range(0, 26)]  # the str() conversion converts str->str and is only necessary to comfort the type checker
            #return [f"{shift}: {self.encode(data, key=str(shift))}" for shift in range(0, 26)]
        else:
            shift = int(key) * (-1) + 26 if key.isnumeric() else 0
            string = data.decode("utf-8")
            #numbers = [ord(c) % 32 for c in string if c.isalpha()]
            #shifted_numbers = [(n + shift - 1 + 26) % 26 + 1 for n in numbers]
            #out = "".join([chr(n + 96) for n in shifted_numbers])
            out = "".join([self.shift_char(c, shift) for c in string])
            return out
    
    def decode(self, string: str, key: str | None = "all") -> bytes | list[bytes]:
        if key is None or not key.isnumeric():
            return [str(self.encode(string.encode("utf-8"), key=str(shift * (-1) + 26))).encode("utf-8") for shift in range(0, 26)]
            #return [f"{shift}: {self.encode(string.encode("utf-8"), key=str(shift * (-1) + 26))}".encode("utf-8") for shift in range(0, 26)]
        else:
            return str(self.encode(string.encode("utf-8"), str(int(key) * (-1) + 26))).encode("utf-8")


class TapCodeCipher(Cipher):
    def __init__(self) -> None:
        super().__init__("Tap")
        self.tap_by_char = {
            'a': "11", 'b': "12", 'c': "13", 'd': "14", 'e': "15",
            'f': "21", 'g': "22", 'h': "23", 'i': "24", 'j': "25",
            'l': "31", 'm': "32", 'n': "33", 'o': "34", 'p': "35",
            'q': "41", 'r': "42", 's': "43", 't': "44", 'u': "45",
            'v': "51", 'w': "52", 'x': "53", 'y': "54", 'z': "55",
            'k': "13"
        }
        self.char_by_tap = { self.tap_by_char[k]: k for k in self.tap_by_char.keys() }

    def encode(self, data: bytes, key: str | None = None) -> str:
        string = data.decode("utf-8")
        out = " ".join([(self.tap_by_char[c] if c in self.tap_by_char else "??") for c in string.lower()])
        return out

    
    def decode(self, string: str, key: str | None = None) -> bytes:
        if not " " in string and len(string) % 2 != 0:
           return "No spaces in string and string of odd length".encode("utf-8")
        
        pairs = string.split(" ") if " " in string else [string[i:i+2] for i in range(0, len(string), 2)]
        out = "".join([(self.char_by_tap[tap] if tap in self.char_by_tap else "?") for tap in pairs])
        return out.encode("utf-8")


class MorseCodeCipher(Cipher):
    def __init__(self) -> None:
        super().__init__("Morse")
        self.morse_by_char = {
            "a": ".-",
            "b": "-...",
            "c": "-.-.",
            "d": "-..",
            "e": ".",
            "f": "..-.",
            "g": "--.",
            "h": "....",
            "i": "..",
            "j": ".---",
            "k": "-.-",
            "l": ".-..",
            "m": "--",
            "n": "-.",
            "o": "---",
            "p": ".--.",
            "q": "--.-",
            "r": ".-.",
            "s": "...",
            "t": "-",
            "u": "..-",
            "v": "...-",
            "w": ".--",
            "x": "-..-",
            "y": "-.--",
            "z": "--..",
            "1": ".----",
            "2": "..---",
            "3": "...--",
            "4": "....-",
            "5": ".....",
            "6": "-....",
            "7": "--...",
            "8": "---..",
            "9": "----.",
            "0": "-----"
        }
        self.char_by_morse = { self.morse_by_char[k]: k for k in self.morse_by_char.keys() }

    def encode(self, data: bytes, key: str | None = None) -> str:
        string = data.decode("utf-8")
        out = " ".join([(self.morse_by_char[c] if c in self.morse_by_char else "???") for c in string.lower()])
        return out
    
    def decode(self, string: str, key: str | None = None) -> bytes:
        symbols = string.split(" ")
        out = "".join([(self.char_by_morse[symbol] if symbol in self.char_by_morse else "?") for symbol in symbols])
        return out.encode("utf-8")

class SMSMultiTapCipher(Cipher):
    def __init__(self) -> None:
        super().__init__("SMS")
        self.mt_by_char = {
            "a": "2",
            "b": "22",
            "c": "222",
            "d": "3",
            "e": "33",
            "f": "333",
            "g": "4",
            "h": "44",
            "i": "444",
            "j": "5",
            "k": "55",
            "l": "555",
            "m": "6",
            "n": "66",
            "o": "666",
            "p": "7",
            "q": "77",
            "r": "777",
            "s": "7777",
            "t": "8",
            "u": "88",
            "v": "888",
            "w": "9",
            "x": "99",
            "y": "999",
            "z": "9999",
            " ": "0"
        }
        self.char_by_mt = { self.mt_by_char[k]: k for k in self.mt_by_char.keys() }

    def encode(self, data: bytes, key: str | None = None) -> str:
        string = data.decode("utf-8")
        out = " ".join([(self.mt_by_char[c] if c in self.mt_by_char else "???") for c in string.lower()])
        return out
    
    def decode(self, string: str, key: str | None = None) -> bytes:
        symbols = string.split(" ")
        out = "".join([(self.char_by_mt[symbol] if symbol in self.char_by_mt else "?") for symbol in symbols])
        return out.encode("utf-8")


t9_lookup_tree_all = T9LookupTree(dictionary_all)
t9_lookup_tree_common = T9LookupTree(dictionary_popular)

class T9Cipher(Cipher):
    def __init__(self) -> None:
        super().__init__("T9")
    
    def decode(self, string: str, key: str | None = None) -> bytes:
        tree = t9_lookup_tree_common if key == "common" else t9_lookup_tree_all

        return tree.lookup(string).encode("utf-8")
    
    def encode(self, data: bytes, key: str | None = None) -> str:
        lookup_table = t9_lookup_tree_all.key_lookup
        return " ".join(["".join([str(lookup_table[c]) if c in lookup_table else "?" for c in s]) for s in data.decode("utf-8").lower().split(" ")])

all_ciphers = [TextCipher(), NumbersCipher(), CaesarCipher(), MorseCodeCipher(), TapCodeCipher(), SMSMultiTapCipher(), HexAsciiCipher(), T9Cipher()]
analysis_ciphers = [NumbersCipher(), CaesarCipher(), MorseCodeCipher(), TapCodeCipher(), SMSMultiTapCipher()]

