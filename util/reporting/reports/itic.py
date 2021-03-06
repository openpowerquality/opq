import matplotlib.pyplot as plt


def percent_nominal(nominal: float, actual: float) -> float:
    return actual / nominal * 100.0


def perecent_nominal_from_zero(nominal: float, actual: float) -> float:
    return percent_nominal(nominal, actual) - 100.0


def cycles_to_s(cycles: float) -> float:
    return cycles / 60.0


def ms_to_s(ms: float) -> float:
    return ms / 1000.0


def ms_to_c(ms: float) -> float:
    return ms * 60.0


def s_to_c(s: float) -> float:
    return s * 1000.0 * 60.0

MAX_X = 30_000_000
MAX_Y = 30_000_000

PROHIBITED_REGION_POLYGON = [
    [0.01, MAX_Y],
    [0.01, 500],
    [ms_to_c(1), 200],
    [ms_to_c(3), 140],
    [ms_to_c(3), 120],
    [ms_to_c(20), 120],
    [ms_to_c(500), 120],
    [ms_to_c(500), 110],
    [ms_to_c(10000), 110],
    [ms_to_c(MAX_X), 110],
    [ms_to_c(MAX_X), MAX_Y],
    [0.01, MAX_Y]
]
"""Polygon representing the prohibited region"""

NO_DAMAGE_REGION_POLYGON = [
    [ms_to_c(20), 0],
    [ms_to_c(20), 40],
    [ms_to_c(20), 70],
    [ms_to_c(500), 70],
    [ms_to_c(500), 80],
    [ms_to_c(10_000), 80],
    [ms_to_c(10_000), 90],
    [ms_to_c(MAX_X), 90],
    [ms_to_c(MAX_X), 0],
    [ms_to_c(20), 0]
]
"""Polygon representing the no damage region"""

NO_INTERRUPTION_REGION_POLYGON = [
    [0, 0],
    [0, MAX_Y],
    [0.01, MAX_Y],
    [0.01, 500],
    [ms_to_c(1), 200],
    [ms_to_c(3), 140],
    [ms_to_c(3), 120],
    [ms_to_c(20), 120],
    [ms_to_c(500), 120],
    [ms_to_c(500), 110],
    [ms_to_c(10_000), 110],
    [ms_to_c(MAX_X), 110],
    [ms_to_c(MAX_X), 90],
    [ms_to_c(10_000), 90],
    [ms_to_c(10_000), 80],
    [ms_to_c(500), 80],
    [ms_to_c(500), 70],
    [ms_to_c(20), 70],
    [ms_to_c(20), 40],
    [ms_to_c(20), 0],
    [0, 0]
]
"""Polygon representing the no interruption region"""


def plot_itic(vrms: float, duration_ms: float):
    max_x = max(s_to_c(15), ms_to_c(duration_ms))
    max_y = max(500, vrms)

    top_x = [.01, ms_to_c(1), ms_to_c(3), ms_to_c(3), ms_to_c(20), s_to_c(.5), s_to_c(.5), s_to_c(10), max_x]
    top_y = [500, 200, 140, 120, 120, 120, 110, 110, 110]

    bottom_x = [ms_to_c(20), ms_to_c(20), ms_to_c(20), s_to_c(.5), s_to_c(.5), s_to_c(10), s_to_c(10), max_x]
    bottom_y = [0, 40, 70, 70, 80, 80, 90, 90]

    plt.figure(figsize=(16, 9))
    plt.xscale("log")
    plt.plot(top_x, top_y, color="red", label="Prohibited Region Bounds")
    plt.plot(bottom_x, bottom_y, color="blue", label="No-Damage Region Bounds")

    plt.scatter([ms_to_c(duration_ms)], [percent_nominal(120.0, vrms)], linewidth=5, color="black", label="ITIC Value")

    plt.title("ITIC $V_{RMS}$=%.1f, Duration MS=%.1f" % (vrms, duration_ms))
    plt.ylim((0, max_y))
    plt.xlim((0, max_x))
    plt.ylabel("% Nominal @ 120V")
    plt.xlabel("Duration Cycles @ 60Hz")

    plt.text(1000, 300, "Prohibited Region", fontsize=12)
    plt.text(.1, 150, "No Interruption Region", fontsize=12)
    plt.text(10000, 30, "No Damage Region", fontsize=12)

    plt.legend()
    plt.show()

if __name__ == "__main__":
    plot_itic(77, 100)
