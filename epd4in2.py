# Compatibility layer for the Waveshare Pico-ePaper-4.2 B driver.
# Keep Pico-ePaper-4.2-B.py beside this file on the Pico filesystem.

try:
    source_file = open("Pico-ePaper-4.2-B.py")
    source_text = source_file.read()
    source_file.close()
    exec(source_text, globals())
except OSError:
    raise ImportError(
        "Pico-ePaper-4.2-B.py is required; copy the official Waveshare file to the Pico"
    )


class EPD4in2:
    """Dashboard-compatible facade over Waveshare's verified B driver."""

    def __init__(self):
        # The official constructor identifies the controller revision, initializes
        # it, and clears the panel using the protocol that works on this hardware.
        self._driver = EPD_4in2_B()
        self.width = EPD_WIDTH
        self.height = EPD_HEIGHT
        self.busy_pin = self._driver.busy_pin
        self.is_v2 = self._driver.flag == 1
        # A blank secondary (red) image produces a B/W dashboard frame.
        self._secondary_image = bytes((0xFF,)) * (EPD_WIDTH * EPD_HEIGHT // 8)

    def init(self):
        # Initialization already occurs in EPD_4in2_B.__init__().
        return None

    def clear(self, color=0xFF):
        if color == 0xFF:
            self._driver.EPD_4IN2B_Clear()
            return
        if color != 0x00:
            raise ValueError("color must be 0x00 (black) or 0xFF (white)")
        image = bytes((color,)) * (EPD_WIDTH * EPD_HEIGHT // 8)
        self.display(image)

    def display(self, image):
        if len(image) != EPD_WIDTH * EPD_HEIGHT // 8:
            raise ValueError("image must contain exactly 15,000 bytes")
        self._driver.EPD_4IN2B_Display(image, self._secondary_image)

    def display_partial(self, image, x=0, y=0, w=EPD_WIDTH, h=EPD_HEIGHT):
        # The supplied driver reliably performs full refreshes.
        self.display(image)

    def sleep(self):
        self._driver.Sleep()
