
class Cipher:
    def __init__(self, name) -> None:
        self.name = name

    def encode(self, data: bytes, key: str = None) -> str:
        return data.decode("utf-8")
    
    def decode(self, string: str, key: str = None) -> bytes:
        return string.encode("utf-8")

class TextCipher(Cipher):
    def __init__(self) -> None:
        super().__init__("Text")

    def encode(self, data: bytes, key: str = None) -> str:
        return data.decode("utf-8")
    
    def decode(self, string: str, key: str = None) -> bytes:
        return string.encode("utf-8")


class NumbersCipher(Cipher):
    def __init__(self) -> None:
        super().__init__("Numbers")

    def encode(self, data: bytes, key: str = None) -> str:
        string = data.decode("utf-8")
        out = " ".join([str(ord(c) % 32) for c in string if c.isalpha()])
        return out
    
    def decode(self, string: str, key: str = None) -> bytes:
        try:
            out = "".join([chr(int(n) % 32 + 96) for n in string.split(" ")])
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


    def encode(self, data: bytes, key: str = None) -> str:
        if not key.isnumeric():
            return "\n".join([f"{shift}: {self.encode(data, key=str(shift))}" for shift in range(0, 26)])
        else:
            shift = int(key) * (-1) + 26 if key.isnumeric() else 0
            string = data.decode("utf-8")
            #numbers = [ord(c) % 32 for c in string if c.isalpha()]
            #shifted_numbers = [(n + shift - 1 + 26) % 26 + 1 for n in numbers]
            #out = "".join([chr(n + 96) for n in shifted_numbers])
            out = "".join([self.shift_char(c, shift) for c in string])
            return out
    
    def decode(self, string: str, key: str = None) -> bytes:
        if not key.isnumeric():
            return "\n".join([f"{shift}: {self.encode(string.encode("utf-8"), key=str(shift * (-1) + 26))}" for shift in range(0, 26)]).encode("utf-8")
        else:
            return self.encode(string.encode("utf-8"), str(int(key) * (-1) + 26)).encode("utf-8")


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

    def encode(self, data: bytes, key: str = None) -> str:
        string = data.decode("utf-8")
        out = " ".join([(self.tap_by_char[c] if c in self.tap_by_char else "??") for c in string])
        return out

    
    def decode(self, string: str, key: str = None) -> bytes:
        if not " " in string and len(string) % 2 != 0:
           return "No spaces in string and string of odd length".encode("utf-8")
        
        pairs = string.split(" ") if " " in string else [string[i:i+2] for i in range(0, len(string), 2)]
        out = "".join([(self.char_by_tap[tap] if tap in self.char_by_tap else "?") for tap in pairs])
        return out.encode("utf-8")


class MorseCodeCipher(Cipher):
    def __init__(self) -> None:
        super().__init__("Morse")

    def encode(self, data: bytes, key: str = None) -> str:
        return data.decode("utf-8")
    
    def decode(self, string: str, key: str = None) -> bytes:
        return string.encode("utf-8")

all_ciphers = [TextCipher(), NumbersCipher(), CaesarCipher(), MorseCodeCipher(), TapCodeCipher()]

