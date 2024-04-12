
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

all_ciphers = [TextCipher(), NumbersCipher()]

