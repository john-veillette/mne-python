"""
===============================================================================
Script 'mne logo'
===============================================================================

This script makes the logo for MNE.
"""
# @author: drmccloy
# Created on Mon Jul 20 11:28:16 2015
# License: BSD-3-Clause

import numpy as np
import os.path as op
import matplotlib.pyplot as plt
from matplotlib import rcParams
from scipy.stats import multivariate_normal
from matplotlib.path import Path
from matplotlib.text import TextPath
from matplotlib.patches import PathPatch, Ellipse, FancyBboxPatch, Rectangle
from matplotlib.colors import LinearSegmentedColormap

# manually set values
dpi = 300
center_fudge = np.array([15, 30])  # compensate for font bounding box padding
tagline_scale_fudge = 0.97  # to get justification right
tagline_offset_fudge = np.array([0, -100.0])

# font, etc
rcp = {
    "font.sans-serif": ["Primetime"],
    "font.style": "normal",
    "font.weight": "black",
    "font.variant": "normal",
    "figure.dpi": dpi,
    "savefig.dpi": dpi,
    "contour.negative_linestyle": "solid",
}
plt.rcdefaults()
rcParams.update(rcp)

# initialize figure (no axes, margins, etc)
fig = plt.figure(1, figsize=(5, 2.25), frameon=False, dpi=dpi)
ax = plt.Axes(fig, [0.0, 0.0, 1.0, 1.0])
ax.set_axis_off()
fig.add_axes(ax)

# fake field data
delta = 0.01
x = np.arange(-8.0, 8.0, delta)
y = np.arange(-3.0, 3.0, delta)
X, Y = np.meshgrid(x, y)
xy = np.array([X, Y]).transpose(1, 2, 0)
Z1 = multivariate_normal.pdf(
    xy, mean=[-5.0, 0.9], cov=np.array([[8.0, 1.0], [1.0, 7.0]]) ** 2
)
Z2 = multivariate_normal.pdf(
    xy, mean=[2.6, -2.5], cov=np.array([[15.0, 2.5], [2.5, 2.5]]) ** 2
)
Z = Z2 - 0.7 * Z1

# color map: field gradient (yellow-red-gray-blue-cyan)
# yrtbc = {
#     'red': ((0, 1, 1), (0.4, 1, 1), (0.5, 0.5, 0.5), (0.6, 0, 0), (1, 0, 0)),
#     'blue': ((0, 0, 0), (0.4, 0, 0), (0.5, 0.5, 0.5), (0.6, 1, 1), (1, 1, 1)),  # noqa
#     'green': ((0, 1, 1), (0.4, 0, 0), (0.5, 0.5, 0.5), (0.6, 0, 0), (1, 1, 1)),  # noqa
# }
yrtbc = {
    "red": ((0.0, 1.0, 1.0), (0.5, 1.0, 0.0), (1.0, 0.0, 0.0)),
    "blue": ((0.0, 0.0, 0.0), (0.5, 0.0, 1.0), (1.0, 1.0, 1.0)),
    "green": ((0.0, 1.0, 1.0), (0.5, 0.0, 0.0), (1.0, 1.0, 1.0)),
    "alpha": (
        (0.0, 1.0, 1.0),
        (0.4, 0.8, 0.8),
        (0.5, 0.2, 0.2),
        (0.6, 0.8, 0.8),
        (1.0, 1.0, 1.0),
    ),
}
# color map: field lines (red | blue)
redbl = {
    "red": ((0.0, 1.0, 1.0), (0.5, 1.0, 0.0), (1.0, 0.0, 0.0)),
    "blue": ((0.0, 0.0, 0.0), (0.5, 0.0, 1.0), (1.0, 1.0, 1.0)),
    "green": ((0.0, 0.0, 0.0), (1.0, 0.0, 0.0)),
    "alpha": ((0.0, 0.4, 0.4), (1.0, 0.4, 0.4)),
}
mne_field_grad_cols = LinearSegmentedColormap("mne_grad", yrtbc)
mne_field_line_cols = LinearSegmentedColormap("mne_line", redbl)

# plot gradient and contour lines
im = ax.imshow(Z, cmap=mne_field_grad_cols, aspect="equal", zorder=1)
cs = ax.contour(Z, 9, cmap=mne_field_line_cols, linewidths=1, zorder=1)
xlim, ylim = ax.get_xbound(), ax.get_ybound()
plot_dims = np.r_[np.diff(xlim), np.diff(ylim)]
rect = Rectangle(
    [xlim[0], ylim[0]], plot_dims[0], plot_dims[1], facecolor="w", zorder=0.5
)

# create MNE clipping mask
mne_path = TextPath((0, 0), "MNE")
dims = mne_path.vertices.max(0) - mne_path.vertices.min(0)
vert = mne_path.vertices - dims / 2.0
mult = (plot_dims / dims).min()
mult = [mult, -mult]  # y axis is inverted (origin at top left)
offset = plot_dims / 2.0 - center_fudge
mne_clip = Path(offset + vert * mult, mne_path.codes)
ax.add_patch(PathPatch(mne_clip, color="w", zorder=0, linewidth=0))
# apply clipping mask to field gradient and lines
im.set_clip_path(mne_clip, transform=im.get_transform())
ax.add_patch(rect)
rect.set_clip_path(mne_clip, transform=im.get_transform())
for coll in cs.collections:
    coll.set_clip_path(mne_clip, transform=im.get_transform())
# get final position of clipping mask
mne_corners = mne_clip.get_extents().corners()

# add tagline
rcParams.update({"font.sans-serif": ["Cooper Hewitt"], "font.weight": "300"})
tag_path = TextPath((0, 0), "MEG + EEG  ANALYSIS & VISUALIZATION")
dims = tag_path.vertices.max(0) - tag_path.vertices.min(0)
vert = tag_path.vertices - dims / 2.0
mult = tagline_scale_fudge * (plot_dims / dims).min()
mult = [mult, -mult]  # y axis is inverted
offset = (
    mne_corners[-1]
    - np.array([mne_clip.get_extents().size[0] / 2.0, -dims[1]])
    - tagline_offset_fudge
)
tag_clip = Path(offset + vert * mult, tag_path.codes)
tag_patch = PathPatch(tag_clip, facecolor="k", edgecolor="none", zorder=10)
ax.add_patch(tag_patch)
yl = ax.get_ylim()
yy = np.max([tag_clip.vertices.max(0)[-1], tag_clip.vertices.min(0)[-1]])
ax.set_ylim(np.ceil(yy), yl[-1])

# only save actual image extent plus a bit of padding
plt.draw()
static_dir = op.join(op.dirname(__file__), "..", "doc", "_static")
assert op.isdir(static_dir)
plt.savefig(op.join(static_dir, "mne_logo.svg"), transparent=True)
tag_patch.set_facecolor("w")
rect.set_facecolor("0.5")
plt.savefig(op.join(static_dir, "mne_logo_dark.svg"), transparent=True)
tag_patch.set_facecolor("k")
rect.set_facecolor("w")

# modify to make the splash screen
data_dir = op.join(op.dirname(__file__), "..", "mne", "icons")
ax.patches[-1].set_facecolor("w")
for coll in list(ax.collections):
    coll.remove()
bounds = np.array(
    [
        [mne_path.vertices[:, ii].min(), mne_path.vertices[:, ii].max()]
        for ii in range(2)
    ]
)
bounds *= plot_dims / dims
xy = np.mean(bounds, axis=1) - [100, 0]
r = np.diff(bounds, axis=1).max() * 1.2
w, h = r, r * (2 / 3)
box_xy = [xy[0] - w * 0.5, xy[1] - h * (2 / 5)]
ax.set_ylim(box_xy[1] + h * 1.001, box_xy[1] - h * 0.001)
patch = FancyBboxPatch(
    box_xy,
    w,
    h,
    clip_on=False,
    zorder=-1,
    fc="k",
    ec="none",
    alpha=0.75,
    boxstyle="round,rounding_size=200.0",
    mutation_aspect=1,
)
ax.add_patch(patch)
fig.set_size_inches((512 / dpi, 512 * (h / w) / dpi))
plt.savefig(op.join(data_dir, "mne_splash.png"), transparent=True)
patch.remove()

# modify to make an icon
ax.patches.pop(-1)  # no tag line for our icon
patch = Ellipse(xy, r, r, clip_on=False, zorder=-1, fc="k")
ax.add_patch(patch)
ax.set_ylim(xy[1] + r / 1.9, xy[1] - r / 1.9)
fig.set_size_inches((256 / dpi, 256 / dpi))
# Qt does not support clip paths in SVG rendering so we have to use PNG here
# then use "optipng -o7" on it afterward (14% reduction in file size)
plt.savefig(op.join(data_dir, "mne_default_icon.png"), transparent=True)
plt.close()

# 188x45 image
dpi = 96  # for SVG it's different
w_px = 188
h_px = 45
center_fudge = np.array([60, 0])
scale_fudge = 2.1
rcParams.update({"font.sans-serif": ["Primetime"], "font.weight": "black"})
x = np.linspace(-1.0, 1.0, w_px // 2)
y = np.linspace(-1.0, 1.0, h_px // 2)
X, Y = np.meshgrid(x, y)
# initialize figure (no axes, margins, etc)
fig = plt.figure(
    1, figsize=(w_px / dpi, h_px / dpi), facecolor="k", frameon=False, dpi=dpi
)
ax = plt.Axes(fig, [0.0, 0.0, 1.0, 1.0])
ax.set_axis_off()
fig.add_axes(ax)
# plot rainbow
ax.imshow(X, cmap=mne_field_grad_cols, aspect="equal", zorder=1)
ax.imshow(np.ones_like(X) * 0.5, cmap="Greys", aspect="equal", zorder=0, clim=[0, 1])
plot_dims = np.r_[np.diff(ax.get_xbound()), np.diff(ax.get_ybound())]
# MNE text in white
mne_path = TextPath((0, 0), "MNE")
dims = mne_path.vertices.max(0) - mne_path.vertices.min(0)
vert = mne_path.vertices - dims / 2.0
mult = scale_fudge * (plot_dims / dims).min()
mult = [mult, -mult]  # y axis is inverted (origin at top left)
offset = (
    np.array([scale_fudge, 1.0]) * np.array([-dims[0], plot_dims[-1]]) / 2.0
    - center_fudge
)
mne_clip = Path(offset + vert * mult, mne_path.codes)
mne_patch = PathPatch(mne_clip, facecolor="0.5", edgecolor="none", zorder=10)
ax.add_patch(mne_patch)
# adjust xlim and ylim
mne_corners = mne_clip.get_extents().corners()
xmin, ymin = np.min(mne_corners, axis=0)
xmax, ymax = np.max(mne_corners, axis=0)
xl = ax.get_xlim()
yl = ax.get_ylim()
xpad = np.abs(np.diff([xmin, xl[1]])) / 20.0
ypad = np.abs(np.diff([ymax, ymin])) / 20.0
ax.set_xlim(xmin - xpad, xl[1] + xpad)
ax.set_ylim(ymax + ypad, ymin - ypad)
plt.draw()
plt.savefig(op.join(static_dir, "mne_logo_small.svg"), dpi=dpi, transparent=True)
plt.close()
