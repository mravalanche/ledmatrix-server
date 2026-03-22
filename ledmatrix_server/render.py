from PIL import Image
from pathlib import Path
from abc import ABC
from dataclasses import dataclass
from bdfparser import Font as BDFFont
from bdfparser import Bitmap

from ledmatrix_server.resources.loader import get_font


# -------------------------
# Classes
# -------------------------

class Font:
    tiny=BDFFont(get_font("CG-pixel-4x5-mono.bdf"))
    small=BDFFont(get_font("tb-8.bdf"))
    medium=BDFFont(get_font("Dina_r400-6.bdf"))
    large=BDFFont(get_font("10x20_reduced-20.bdf"))


@dataclass
class DisplayComponent(ABC):
    x: int = 0
    y: int = 0
    z: int = 0


@dataclass
class TextComponent(DisplayComponent):
    text: str = ""
    font: BDFFont = Font.tiny
    colour:int = 0xffffff


@dataclass
class ImageComponent(DisplayComponent):
    file: Path|str = ""

    @property
    def image(self):
        return Image.open(self.file).convert(("RGBA"))


class Display():
    def __init__(self, width: int = 64, height: int = 32, output: Path = Path("display")):
        self.width: int = width
        self.height: int = height
        self.output = output
        self.canvas: Image.Image = self._init_canvas()
        self.dirty: bool = True
        self.components: dict[str, DisplayComponent] = dict()

    def _init_canvas(self) -> Image.Image:
        return Image.new("RGBA", (self.width, self.height), "black")
    
    def set(self, name:str, component:DisplayComponent):
        self.components[name] = component
        self.dirty = True
    
    def export(self, format="BMP"):
        output = self.output.with_suffix(f".{format.lower()}")
        self.canvas.save(output, format)
    
    @staticmethod
    def _int_to_rgba(colour: int) -> tuple[int, int, int, int]:
        r = (colour >> 16) & 0xff
        g = (colour >> 8) & 0xff
        b = colour & 0xff
        return (r ,g, b, 255)

    def _render_text_component(self, c: TextComponent):
        bitmap:Bitmap = c.font.draw(c.text)
        rgba:bytes = bitmap.tobytes(mode="RGBA")

        text_img = Image.frombytes(
            "RGBA",
            (bitmap.width(), bitmap.height()),
            rgba
        )
        
        alpha = text_img.getchannel("A")
        colour = self._int_to_rgba(c.colour)
        coloured = Image.new("RGBA", text_img.size, colour)
        coloured.putalpha(alpha)

        self.canvas.alpha_composite(coloured, (c.x, c.y))
    
    def render(self):
        if not self.dirty:
            return
        
        self._init_canvas()

        for _, c in self.components.items():
            if isinstance(c, ImageComponent):
                img = c.image
                self.canvas.paste(img, (c.x, c.y), img)

            if isinstance(c, TextComponent):
                self._render_text_component(c)                
        
        self.dirty = False
    
    def print_to_console(self, scale:int = 1):
        self.render()

        render_width: int = self.width*scale
        render_height: int = int(self.height * render_width / self.width)
        img = self.canvas.resize((render_width, render_height))
        img = img.convert("RGB")

        # Because consoles render characters, this usese half blocks to render what I need
        for y in range(0, img.height, 2):
            for x in range(img.width):
                top = img.getpixel((x, y))
                bottom = img.getpixel((x, y + 1)) if y + 1 < img.height else (0, 0, 0)

                print(
                    f"\x1b[38;2;{top[0]};{top[1]};{top[2]}m" # type: ignore
                    f"\x1b[48;2;{bottom[0]};{bottom[1]};{bottom[2]}m" # type: ignore
                    "▀",
                    end=""
                )
            print("\x1b[0m")

