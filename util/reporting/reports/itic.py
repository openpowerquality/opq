import matplotlib.pyplot as plt


def percent_nominal(nominal: float, actual: float) -> float:
    return actual / nominal * 100.0


def perecent_nominal_from_zero(nominal: float, actual: float) -> float:
    return percent_nominal(nominal, actual) - 100.0


def cycles_to_s(cycles: float) -> float:
    return cycles / 60.0


def ms_to_s(ms: float) -> float:
    return ms / 1000.0


def plot_itic(vrms: float, duration_ms: float):
    x_values = list(range(15))

    top_bounds_x = [cycles_to_s(.01), ms_to_s(3), ms_to_s(1), ms_to_s(1), ms_to_s(20), .5,  .5,  10]
    top_bounds_y = [500,              200,        140,        120,        120,         120, 110, 110]

    plt.figure(figsize=(16,9))
    plt.plot(top_bounds_x, top_bounds_y)

    plt.show()

if __name__ == "__main__":
    plot_itic(0, 0)
