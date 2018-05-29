import collections
import matplotlib.pyplot as plt


margin_l_absolute = 8. * 0.1
margin_r_absolute = 8. * 0.02
margin_sep_absolute = 8. * 0.02
margin_t_absolute = 8. * 0.02
margin_t_absolute_extra = 8. * 0.12
margin_b_absolute = 8. * 0.08


def calculate_height(
    n_panels=2, width=8., panel_aspect_ratio=1., extra_top_space=False
):
    if isinstance(n_panels, collections.Sequence):
        n_panels_h, n_panels_v = n_panels
    else:
        n_panels_h = n_panels
        n_panels_v = 1

    # Determine top margin
    _margin_t_absolute = (
        margin_t_absolute_extra if extra_top_space else margin_t_absolute
    )

    # Calculate horizontal margins. Units: relative to width.
    margin_l = margin_l_absolute / width
    margin_r = margin_r_absolute / width
    margin_l_subsequent = margin_l
    if n_panels_h > 2:
        margin_l_subsequent = margin_r

    margin_sep = margin_sep_absolute / width
    if n_panels_h > 2:
        margin_sep = 0

    margin_sep_total = margin_r + margin_sep + margin_l_subsequent
    panel_width = (
        1. - margin_l - margin_r - (n_panels_h - 1) * margin_sep_total
    ) / n_panels_h

    # Calculate absolute height
    panel_height_absolute = panel_width * width / panel_aspect_ratio
    height = (
        n_panels_v * (panel_height_absolute + _margin_t_absolute + margin_b_absolute)
        + (n_panels_v - 1) * margin_sep_absolute
    )

    # Calculate horizontal margins. Units: relative to width.
    panel_height = panel_height_absolute / height
    margin_t = _margin_t_absolute / height
    margin_b = margin_b_absolute / height
    margin_sep_total = margin_t + margin_b + margin_sep_absolute / height

    # Return height
    return height


def adjust_margins(n_panels=2, width=8., panel_aspect_ratio=1., extra_top_space=False):
    if isinstance(n_panels, collections.Sequence):
        n_panels_h, n_panels_v = n_panels
    else:
        n_panels_h = n_panels
        n_panels_v = 1

    # Determine top margin
    _margin_t_absolute = (
        margin_t_absolute_extra if extra_top_space else margin_t_absolute
    )

    # Calculate horizontal margins. Units: relative to width.
    margin_l = margin_l_absolute / width
    margin_r = margin_r_absolute / width
    margin_l_subsequent = margin_l
    if n_panels_h > 2:
        margin_l_subsequent = margin_r
    margin_sep = margin_sep_absolute / width
    if n_panels_h > 2:
        margin_sep = 0
    margin_sep_total = margin_r + margin_sep + margin_l_subsequent
    panel_width = (
        1. - margin_l - margin_r - (n_panels_h - 1) * margin_sep_total
    ) / n_panels_h

    # Calculate wspace argument of subplots_adjust
    wspace = margin_sep_total / panel_width

    # Calculate absolute height
    panel_height_absolute = panel_width * width / panel_aspect_ratio
    height = (
        n_panels_v * (panel_height_absolute + _margin_t_absolute + margin_b_absolute)
        + (n_panels_v - 1) * margin_sep_absolute
    )

    # Calculate horizontal margins. Units: relative to width.
    panel_height = panel_height_absolute / height
    margin_t = _margin_t_absolute / height
    margin_b = margin_b_absolute / height
    margin_sep_total = margin_t + margin_b + margin_sep_absolute / height

    # Calculate wspace argument of subplots_adjust
    hspace = margin_sep_total / panel_height

    # Set margins
    plt.subplots_adjust(
        left=margin_l,
        right=1. - margin_r,
        bottom=margin_b,
        top=1. - margin_t,
        wspace=wspace,
        hspace=hspace,
    )
