import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib

filename = "./test/data/main-eval/properties"
algorithms = ["pho-ip", "lsh", "ilsh", "pho-lp"]
abbreviations = {
    "pho-ip": "$h^{pho}$",
    "pho-lp": "$h^{pho}_{LP}$",
    "lsh": "$h^{pho}_{lsh}$",
    "ilsh": "$\\mathbf{h}^{\\mathbf{pho}}_{\\mathbf{ilsh}}$",
}
sys_types = ["sys2", "sys4"]
cost_types = ["one", "normal"]
rows_labels = ["2U", "4U", "2N", "4N"]
initial_heuristic_values_by_sys_type_and_instance = {
    sys: {type: {} for type in cost_types} for sys in sys_types
}
plots = [("pho-ip", "pho-lp"), ("pho-ip", "ilsh"), ("pho-ip", "lsh"), ("lsh", "ilsh")]
matplotlib.rcParams["axes.prop_cycle"] = matplotlib.cycler(
    color=["gray", "#1f77b4", "#b4301f"]
)
plt.minorticks_off()


def extract_initial_value_for_algorithms(
    algorithms: list[str], domain: str, problem: str, sys: str, type: str
):
    response = {}
    target = f"{sys}-{type}-{domain}-{problem}"
    for key in properties.keys():
        if not target in key:
            continue
        for alg in algorithms:
            if f"-{alg}-" not in key:
                continue
            response[alg] = properties[key]["initial_h_value"]

    return response


with open(filename) as file:
    properties: dict[str, object] = json.load(file)
    for key in properties.keys():
        if "pho-ip" not in key:  # I see what you did here
            continue

        domain = properties[key]["domain"]
        problem = properties[key]["problem"]

        for sys in initial_heuristic_values_by_sys_type_and_instance.keys():
            for type in initial_heuristic_values_by_sys_type_and_instance[sys]:
                initial_heuristic_values_by_sys_type_and_instance[sys][type][
                    f"{domain}:{problem}"
                ] = extract_initial_value_for_algorithms(
                    algorithms, domain, problem, sys, type
                )

row_index = -1
plt.clf()
plt.figure(figsize=(7, 7), dpi=600)
for type in cost_types:
    limit = 10**2
    for sys in sys_types:
        row_index += 1
        column_index = -1
        for plot in plots:
            number_in, number_out = 0, 0
            first_alg = plot[0]
            second_alg = plot[1]
            column_index += 1
            ax = plt.subplot2grid(
                (len(plots), len(cost_types) * len(sys_types)),
                (row_index, column_index),
            )
            xpoints = np.array(
                [
                    initial_h_values[first_alg]
                    for initial_h_values in initial_heuristic_values_by_sys_type_and_instance[
                        sys
                    ][
                        type
                    ].values()
                ]
            )
            ypoints = np.array(
                [
                    initial_h_values[second_alg]
                    for initial_h_values in initial_heuristic_values_by_sys_type_and_instance[
                        sys
                    ][
                        type
                    ].values()
                ]
            )
            for x, y in zip(xpoints, ypoints):
                if x > limit or y > limit or x < 1 or y < 1:
                    number_out += 1
                else:
                    number_in += 1

                if column_index == 1:
                    if y / x > 1.5:
                        print(y, x, y / x)

            # plt.title(f"{first_alg}-{second_alg}-{sys}", fontsize=8)

            plt.xscale("log")
            plt.yscale("log")
            plt.xlim(1, limit)
            plt.ylim(1, limit)
            if row_index == 0:
                plt.xlabel(
                    f"{abbreviations[first_alg]} vs {abbreviations[second_alg]}",
                    fontsize=12,
                    labelpad=10,
                )
                ax.xaxis.set_label_position("top")
            if column_index == len(cost_types) * len(sys_types) - 1:
                plt.ylabel(rows_labels[row_index], fontsize=12, rotation=0, labelpad=14)
                ax.yaxis.set_label_position("right")
            if row_index != len(plots) - 1:
                plt.xticks([], [])
            if column_index != 0:
                plt.yticks([], [])
            ax.set_aspect("equal", adjustable="box")
            plt.plot(
                (0, limit),
                (0, limit),
                c="black",
                ls=":",
                lw=1,
            )
            plt.scatter(xpoints, ypoints, alpha=0.08, s=10, c="black")
            print(
                f"in: {number_in} - out: {number_out} | {type}/{sys} | {first_alg} x {second_alg}"
            )
plt.tight_layout()
plt.savefig(f"test.png")
