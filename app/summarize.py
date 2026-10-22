"""Summarise gene findings into figures.

CLI:
    python -m app.summarize --input data/findings.json --out figures/
"""

import argparse
import json
import os
import sys

import matplotlib

matplotlib.use("Agg")  # non-interactive backend

import matplotlib.pyplot as plt  # noqa: E402
import networkx as nx  # noqa: E402


def load_findings(path):
    """Load and validate the findings JSON file."""
    if not os.path.isfile(path):
        raise SystemExit(f"ERROR: input file not found: {path}")
    try:
        with open(path) as fh:
            data = json.load(fh)
    except (json.JSONDecodeError, OSError) as exc:
        raise SystemExit(f"ERROR: could not parse input file {path}: {exc}")
    for key in ("gene", "diseases", "interactions", "structures"):
        if key not in data:
            raise SystemExit(f"ERROR: input file {path} is missing required key '{key}'")
    return data


def plot_diseases(data, gene, outpath):
    """Horizontal bar chart of disease association scores, sorted descending."""
    items = sorted(data["diseases"], key=lambda d: d["score"], reverse=True)
    names = [d["name"] for d in items]
    scores = [d["score"] for d in items]
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.barh(range(len(names)), scores, color="#4C72B0")
    ax.set_yticks(range(len(names)))
    ax.set_yticklabels(names)
    ax.invert_yaxis()
    ax.set_xlabel("Association score")
    ax.set_title(f"{gene} - Top disease associations")
    fig.tight_layout()
    fig.savefig(outpath, dpi=150)
    plt.close(fig)


def plot_interactions(data, gene, outpath):
    """Star network with the gene at the centre and partners around it."""
    g = nx.Graph()
    g.add_node(gene, role="gene")
    for it in data["interactions"]:
        g.add_node(it["partner"], role="partner")
        g.add_edge(gene, it["partner"], weight=it["score"])
    pos = nx.spring_layout(g, seed=42)
    fig, ax = plt.subplots(figsize=(8, 8))
    weights = [g[u][v]["weight"] for u, v in g.edges()]
    nx.draw_networkx_nodes(
        g, pos,
        nodelist=[gene], node_color="#C44E52", node_size=1200, ax=ax, label="Gene",
    )
    nx.draw_networkx_nodes(
        g, pos,
        nodelist=[n for n in g.nodes if n != gene],
        node_color="#55A868", node_size=700, ax=ax, label="Partner",
    )
    nx.draw_networkx_edges(g, pos, width=[w * 6 for w in weights], ax=ax, edge_color="#8C8C8C")
    nx.draw_networkx_labels(g, pos, font_size=9, ax=ax)
    ax.set_title(f"{gene} - Interaction partners (edge width = score)")
    ax.legend(loc="best")
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(outpath, dpi=150)
    plt.close(fig)


def plot_structures(data, gene, outpath):
    """Two panels: entries per method (bar) and resolution distribution (histogram)."""
    entries = data["structures"]["entries"]
    fig, axs = plt.subplots(1, 2, figsize=(12, 5))
    if not entries:
        for ax in axs:
            ax.text(0.5, 0.5, "No experimental structures found",
                    ha="center", va="center", transform=ax.transAxes)
            ax.set_axis_off()
        axs[0].set_title(f"{gene} - Structures")
        fig.tight_layout()
        fig.savefig(outpath, dpi=150)
        plt.close(fig)
        return

    methods = {}
    for e in entries:
        methods[e["method"]] = methods.get(e["method"], 0) + 1
    method_names = sorted(methods)
    counts = [methods[m] for m in method_names]
    axs[0].bar(method_names, counts, color="#4C72B0")
    axs[0].set_xlabel("Experimental method")
    axs[0].set_ylabel("Number of entries")
    axs[0].set_title(f"{gene} - Structures by method")
    axs[0].tick_params(axis="x", rotation=20)

    resolutions = [e["resolution"] for e in entries if e.get("resolution") is not None]
    if resolutions:
        min_res = min(resolutions)
        max_res = max(resolutions)
        bins = max(10, int(max_res - min_res))
        axs[1].hist(resolutions, bins=bins, color="#55A868", edgecolor="white")
        axs[1].set_xlabel("Resolution (Å)")
        axs[1].set_ylabel("Number of entries")
        axs[1].set_title(f"{gene} - Resolution distribution")
    else:
        axs[1].text(0.5, 0.5, "No resolution data", ha="center", va="center",
                    transform=axs[1].transAxes)
        axs[1].set_axis_off()
        axs[1].set_title(f"{gene} - Resolution distribution")

    fig.tight_layout()
    fig.savefig(outpath, dpi=150)
    plt.close(fig)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Summarise gene findings into figures.")
    parser.add_argument("--input", required=True, help="Path to findings.json")
    parser.add_argument("--out", required=True, help="Output directory for PNG figures")
    args = parser.parse_args(argv)

    data = load_findings(args.input)
    gene = data["gene"]["symbol"]
    os.makedirs(args.out, exist_ok=True)
    outdir = args.out

    plot_diseases(data, gene, os.path.join(outdir, "diseases.png"))
    plot_interactions(data, gene, os.path.join(outdir, "interactions.png"))
    plot_structures(data, gene, os.path.join(outdir, "structures.png"))

    print(f"Wrote figures for {gene} to {outdir}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
