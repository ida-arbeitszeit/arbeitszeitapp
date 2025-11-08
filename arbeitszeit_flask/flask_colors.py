import colorsys


def hsl_to_hex(hue: float, saturation: float, lightness: float) -> str:
    """
    Parameters:
        h (float): Hue angle in degrees (0–360)
        s (float): Saturation (0–100)
        l (float): Lightness (0–100)

    Returns:
        str: Hex color string (e.g. '#ff5733')
    """
    # convert to 0–1 range
    hue /= 360
    saturation /= 100
    lightness /= 100

    r, g, b = colorsys.hls_to_rgb(hue, lightness, saturation)

    # Convert to 0–255 and then to hex
    return "#{:02x}{:02x}{:02x}".format(int(r * 255), int(g * 255), int(b * 255))


class FlaskColors:
    # hsl values must be in sync with colors.css
    @property
    def primary(self):
        return hsl_to_hex(171, 100, 41)

    @property
    def info(self):
        return hsl_to_hex(207, 61, 53)

    @property
    def warning(self):
        return hsl_to_hex(44, 100, 77)

    @property
    def danger(self):
        return hsl_to_hex(348, 86, 61)

    @property
    def success(self):
        return hsl_to_hex(153, 53, 53)
