import rasterio.plot

from gdal_viirs.types import Number
from typing import Tuple, Optional
from rasterio import DatasetReader
from matplotlib import pyplot, patches, offsetbox
import cartopy

_CM = 1/2.54


def cm(v):
    return v * _CM


def build_figure(data, axes, *, xlim: Tuple[Number, Number] = None,
                 ylim: Tuple[Number, Number] = None, scale='10m', cmap=None, norm=None, transform=None):
    axes.set_axis_off()
    if xlim:
        axes.set_xlim(xlim)
    if ylim:
        axes.set_ylim(ylim)

    coastline = cartopy.feature.NaturalEarthFeature(category='physical',
                                                    name='coastline',
                                                    scale=scale,
                                                    facecolor='None')
    minor_islands = cartopy.feature.NaturalEarthFeature(category='physical',
                                                        name='minor_islands',
                                                        scale=scale,
                                                        facecolor='None')
    lakes_contour = cartopy.feature.NaturalEarthFeature(category='physical',
                                                        name='lakes',
                                                        scale=scale,
                                                        facecolor='None')
    admin_0_countries = cartopy.feature.NaturalEarthFeature(category='cultural',
                                                            name='admin_0_countries',
                                                            scale=scale,
                                                            facecolor='None')
    admin_1_states_provinces = cartopy.feature.NaturalEarthFeature(category='cultural',
                                                                   name='admin_1_states_provinces',
                                                                   scale=scale,
                                                                   facecolor='None')

    rasterio.plot.show(data, cmap=cmap, norm=norm, ax=axes, transform=transform, origin='upper',
                       interpolation='nearest')

    axes.add_feature(coastline, edgecolor='black', linewidth=2)
    axes.add_feature(minor_islands, edgecolor='black', linewidth=0.5)
    axes.add_feature(lakes_contour, edgecolor='black', linewidth=0.4)
    axes.add_feature(admin_0_countries, edgecolor='black', linewidth=3)
    axes.add_feature(admin_1_states_provinces, edgecolor='black', linewidth=1, linestyle=':')

    return axes


def plot_marks(points: dict, crs, ax, color='k'):
    plate_carree = cartopy.crs.PlateCarree()
    for coord, text in points.items():
        point = crs.transform_point(coord[0], coord[1], plate_carree)
        ax.plot(*point, color=color, markersize=14, marker='o')
        ax.annotate(text, point, fontsize=25).set_clip_on(True)


def _plot_rect_with_outside_border(image_pos_ax, plot_size_ax, ax):
    frame = patches.Rectangle((*image_pos_ax, 0), *plot_size_ax, facecolor='none')
    offbox = offsetbox.AuxTransformBox(ax.transData)
    offbox.add_artist(frame)
    ab = offsetbox.AnnotationBbox(offbox,
                                  (image_pos_ax[0] + plot_size_ax[0] / 2., image_pos_ax[1] + plot_size_ax[1] / 2.),
                                  boxcoords="data", pad=0.52, fontsize=2,
                                  bboxprops=dict(fc="none", ec='k', lw=2))
    ax.add_artist(ab)


class MapBuilder:
    xlim: Optional[Tuple[Number, Number]]
    ylim: Optional[Tuple[Number, Number]]
    cartopy_scale: str
    cmap = None
    norm = None
    marks_color = 'blue'
    font_size = 25
    outer_size: Tuple[Number, Number, Number, Number] = cm(.5), cm(.5), cm(.5), cm(.5)
    dpi = 100
    max_width = None
    max_height = None

    def __init__(self):
        self._points = {}
        self.xlim = None
        self.ylim = None
        self.cartopy_scale = '10m'

    def add_point(self, lon: Number, lat: Number, text: str):
        self._points[(lon, lat)] = text

    def plot(self, file: DatasetReader, band=1):
        xlim = self.xlim or (file.transform.c, file.transform.a * file.width + file.transform.c)
        ylim = self.ylim or (file.transform.e * file.height + file.transform.f, file.transform.f)
        plot_width = abs(xlim[0] - xlim[1]) / file.transform.a / self.dpi
        plot_height = abs(ylim[0] - ylim[1]) / file.transform.a / self.dpi
        zoom = 1
        if self.max_width is not None:
            zoom = min(zoom, self.max_width / plot_width)
        if self.max_height is not None:
            zoom = min(zoom, self.max_height / plot_height)
        plot_width *= zoom
        plot_height *= zoom

        plot_size = plot_width, plot_height
        data = file.read(band)
        crs = self.get_projection(file)
        figsize = plot_size[0] + self.outer_size[1] + self.outer_size[3], plot_size[1] + self.outer_size[0] + self.outer_size[2]
        fig = pyplot.figure(figsize=figsize, dpi=self.dpi)

        # сконвертировать координаты изображения в пиксели (можно просто помножить на dpi)
        image_pos = self.outer_size[3], self.outer_size[0]  # позиция изображения в дюймах (от верхнего левого угла)
        image_pos_px = fig.dpi_scale_trans.transform((image_pos[0], figsize[1]-image_pos[1]-plot_size[1]))  # позиция изображеня в пикселях, от вернего левого угла
        image_pos_ax = fig.transFigure.inverted().transform(image_pos_px)  # в долях(?) (от 0 до 1)
        plot_size_ax = fig.transFigure.inverted().transform(fig.dpi_scale_trans.transform(plot_size))
        ax0 = fig.add_axes([0, 0, 1, 1])
        ax0.set_axis_off()
        _plot_rect_with_outside_border(image_pos_ax, plot_size_ax, ax0)
        ax1 = fig.add_axes([*image_pos_ax, *plot_size_ax], projection=crs)
        ax1.set_axis_off()
        build_figure(data, ax1, cmap=self.cmap, norm=self.norm, xlim=xlim, ylim=ylim, transform=file.transform)
        plot_marks(self._points, crs, ax1, color=self.marks_color)

        return fig, (ax0, ax1), plot_size

    def plot_to_file(self, file: DatasetReader, output_file: str, band=1):
        figure, _1, _2 = self.plot(file, band)
        figure.savefig(output_file, bbox_inches=None, pad_inches=0, transparent=False)

    def get_projection(self, file):
        return cartopy.crs.PlateCarree()




