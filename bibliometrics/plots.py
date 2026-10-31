"""Radar chart of the thematic axes and drawing of the co-occurrence network."""

import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "DejaVu Serif"],
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.15,
    "savefig.facecolor": "white",
})

DARK = "#0D3F63"
TEXT = "#1A2030"
GRID = "#C8D8E8"
NODE_COLORS = ["#2778AA", "#3A7D60", "#8B4A6E", "#4E6FA8", "#A05C2C", "#5B7A3D",
               "#6B5B95", "#2E7D7A", "#8A6030", "#3D6878", "#7A4060", "#4A7A50"]


def save(fig, path):
    """Save the figure as PDF and PNG (`path` without extension)."""
    for ext in ("pdf", "png"):
        fig.savefig(f"{path}.{ext}")
    plt.close(fig)


def radar(counts, labels, path, step=50, label_size=19, value_size=15):
    """Radar chart with the number of documents of each axis."""
    names = list(counts)
    values = [counts[n] for n in names]
    angles = np.linspace(0, 2 * np.pi, len(names), endpoint=False)
    ticks = np.arange(step, max(values) + step, step)
    r_max = ticks[-1] * 1.10

    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(projection="polar")
    ax.set_ylim(0, r_max)
    ax.set_rlabel_position(45)
    ax.set_yticks(ticks, [str(t) for t in ticks], color="#5A8AAA", fontsize=10)
    ax.set_xticks(angles, [])
    ax.spines["polar"].set_visible(False)
    ax.grid(False)

    circle = np.linspace(0, 2 * np.pi, 200)
    for t in ticks:
        ax.plot(circle, np.full_like(circle, t), color=GRID, lw=0.8, zorder=1)
    for a in angles:
        ax.plot([a, a], [0, r_max], color=GRID, lw=0.8, zorder=1)

    closed_angles = np.append(angles, angles[0])
    closed_values = values + values[:1]
    ax.fill(closed_angles, closed_values, color="#1A5C8A", alpha=0.18, zorder=2)
    ax.plot(closed_angles, closed_values, color=DARK, lw=2.4, zorder=3)
    ax.scatter(angles, values, s=70, color=DARK, edgecolors="white", linewidths=1.4, zorder=4)

    for angle, name, value in zip(angles, names, values):
        ax.text(angle, ticks[-1] * 1.38, labels.get(name, name), ha="center", va="center",
                fontsize=label_size, fontweight="bold", color=TEXT, zorder=5,
                bbox=dict(boxstyle="round,pad=0.35", facecolor="#F0F5FA", edgecolor="#C0D0E0",
                          linewidth=0.7, alpha=0.9))
        # values inside the polygon, or just outside small ones
        r_text = value * 0.62 if value > ticks[-1] * 0.15 else value + ticks[-1] * 0.08
        if value > 0:
            ax.text(angle, r_text, str(value), ha="center", va="center", fontsize=value_size,
                    fontweight="bold", color=DARK, zorder=6)

    fig.tight_layout()
    save(fig, path)


def network_layout(graph, sizes, seed=42, stretch=1.6):
    """Spring layout followed by removal of node overlaps.

    The positions are normalised to [-stretch, stretch] x [-1, 1] so that the
    network fills a landscape figure.
    """
    nodes = list(graph.nodes)
    raw = nx.spring_layout(graph, k=7.0 / np.sqrt(len(nodes)), seed=seed, iterations=500, weight=None)
    pos = {n: np.array(raw[n], dtype=float) for n in nodes}
    radius = {n: np.sqrt(sizes[n]) / 2 * 0.18 / 100 for n in nodes}

    for _ in range(300):
        moved = False
        for i, a in enumerate(nodes):
            for b in nodes[i + 1:]:
                d = pos[b] - pos[a]
                dist = np.hypot(*d)
                min_dist = radius[a] + radius[b] + 0.18
                if 1e-9 < dist < min_dist:
                    push = d / dist * (min_dist - dist) / 2
                    pos[a] -= push
                    pos[b] += push
                    moved = True
        if not moved:
            break

    xy = np.array([pos[n] for n in nodes])
    low, span = xy.min(axis=0), np.ptp(xy, axis=0)
    span[span == 0] = 1.0
    scaled = (xy - low) / span * 2 - 1
    scaled[:, 0] *= stretch
    return {n: scaled[i] for i, n in enumerate(nodes)}


def place_label(node, graph, pos, sizes, ax, fig_size, margin=6):
    """Choose the side of the node for its label.

    Each of the eight directions around the node is scored by its overlap
    with the other nodes and by its angle to the direction pointing away from
    the neighbours; the lowest score is kept.
    """
    directions = [(1, 0, "left", "center"), (1, 1, "left", "bottom"), (0, 1, "center", "bottom"),
                  (-1, 1, "right", "bottom"), (-1, 0, "right", "center"), (-1, -1, "right", "top"),
                  (0, -1, "center", "top"), (1, -1, "left", "top")]
    width_pt, height_pt = fig_size[0] * 72, fig_size[1] * 72
    x_range = np.diff(ax.get_xlim())[0]
    y_range = np.diff(ax.get_ylim())[0]
    data_per_pt = (x_range / width_pt + y_range / height_pt) / 2
    offset_pt = np.sqrt(sizes[node]) / 2 + margin

    neighbours = list(graph.neighbors(node))
    away = pos[node] - np.mean([pos[n] for n in neighbours], axis=0) if neighbours else pos[node]
    away_angle = np.arctan2(away[1], away[0])

    def overlap(dx, dy):
        label = pos[node] + np.array([dx * offset_pt / width_pt * x_range,
                                      dy * offset_pt / height_pt * y_range])
        total = 0.0
        for other in graph.nodes:
            if other == node:
                continue
            reach = np.sqrt(sizes[other]) / 2 * data_per_pt * 1.5
            dist = np.hypot(*(label - pos[other]))
            if dist < reach:
                total += (1 - dist / reach) ** 2 * 500
        return total

    def score(direction):
        dx, dy = direction[:2]
        diff = abs(np.arctan2(dy, dx) - away_angle)
        return overlap(dx, dy) + min(diff, 2 * np.pi - diff) * 0.4

    dx, dy, ha, va = min(directions, key=score)
    return (dx * offset_pt, dy * offset_pt), ha, va


def network(graph, path, size_range=(7500, 12000), label_size=24, fig_size=(18, 11)):
    """Co-occurrence network.

    Node area grows with the citations accumulated by the keyword, and edge
    width and opacity with the number of co-occurrences.
    """
    nodes = list(graph.nodes)
    citations = {n: max(graph.nodes[n]["citations"], 1) for n in nodes}
    top = max(citations.values())
    low, high = size_range
    sizes = {n: low + (high - low) * (citations[n] / top) ** 0.65 for n in nodes}
    pos = network_layout(graph, sizes)

    fig, ax = plt.subplots(figsize=fig_size)
    ax.set_facecolor("#FAFBFC")
    ax.axis("off")
    xy = np.array(list(pos.values()))
    pad = np.ptp(xy, axis=0) * np.array([0.12, 0.14])
    ax.set_xlim(xy[:, 0].min() - pad[0], xy[:, 0].max() + pad[0])
    ax.set_ylim(xy[:, 1].min() - pad[1], xy[:, 1].max() + pad[1])

    heaviest = max(w for _, _, w in graph.edges(data="weight"))
    for u, v, w in graph.edges(data="weight"):
        ratio = w / heaviest
        ax.plot(*zip(pos[u], pos[v]), color="black", lw=1.2 + 7.5 * ratio ** 0.5,
                alpha=0.18 + 0.72 * ratio, solid_capstyle="round", zorder=1)

    for i, n in enumerate(nodes):
        ax.scatter(*pos[n], s=sizes[n], color=NODE_COLORS[i % len(NODE_COLORS)], edgecolors=DARK,
                   linewidths=1.8, alpha=0.92, zorder=3)

    for n in nodes:
        offset, ha, va = place_label(n, graph, pos, sizes, ax, fig_size)
        words = n.split()
        label = n if len(words) < 3 else (" ".join(words[:(len(words) + 1) // 2]) + "\n"
                                          + " ".join(words[(len(words) + 1) // 2:]))
        ax.annotate(label, xy=pos[n], xytext=offset, textcoords="offset points", ha=ha, va=va,
                    fontsize=label_size, fontweight="bold", color="#0D1A2A", linespacing=1.25,
                    annotation_clip=False, zorder=6,
                    path_effects=[pe.withStroke(linewidth=6, foreground="white")])

    fig.tight_layout()
    save(fig, path)
