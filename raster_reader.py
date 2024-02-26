import argparse

import matplotlib.pyplot as plt
import rasterio


def plot_raster(
    tiff_file: str,
    title: str = None,
    cmap: str = "viridis",
    colorbar_label: str = "Value",
) -> None:
    """
    Plots a raster TIFF file using matplotlib.

    Parameters:
    tiff_file (str): Path to the TIFF file.
    title (str): Title of the plot.
    cmap (str): Colormap for the raster plot.
    colorbar_label (str): Label for the colorbar.
    """
    with rasterio.open(tiff_file) as src:
        raster = src.read(1)  # Read the first band

    plt.figure(figsize=(8, 6))
    plt.imshow(raster, cmap=cmap)
    plt.colorbar(label=colorbar_label)
    plt.title(title if title else "Raster Plot")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.show()


def main():
    parser = argparse.ArgumentParser(description="Plot a raster TIFF file.")
    parser.add_argument("tiff_file", type=str, help="Path to the TIFF file.")
    parser.add_argument("--title", type=str, help="Title of the plot.", default=None)
    parser.add_argument(
        "--cmap", type=str, help="Colormap for the raster plot.", default="viridis"
    )
    parser.add_argument(
        "--colorbar_label", type=str, help="Label for the colorbar.", default="Value"
    )

    args = parser.parse_args()
    plot_raster(args.tiff_file, args.title, args.cmap, args.colorbar_label)


if __name__ == "__main__":
    main()
