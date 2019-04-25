DISPLAY_SPLASH = "DISPLAY_SPLASH"
DISPLAY_AP = "DISPLAY_AP"
DISPLAY_NORMAL = "DISPLAY_NORMAL"

DISPLAY_TYPES = [DISPLAY_SPLASH, DISPLAY_AP, DISPLAY_NORMAL]


def is_display_type(display_type):
    return display_type in DISPLAY_TYPES


def max_size():
    return max(list(map(len, DISPLAY_TYPES)))

