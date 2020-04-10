"""quick workaround for comparing variables from different WRF runs

To do this right (TM) I need to figure out if/how I can generate
panel.depends decorators dynamically.  I haven't figured out the
syntax for that yet and I need these plots for the group meeting this
afternoon, so I'm going with copy/paste for the moment.

"""

import geoviews_tools as gt
import hvplot.xarray

import sys
import numpy as np
import xarray as xr
import panel as pn
import pandas as pd


# gather data

# use local data
ctlday, ytrday, ctl_minus_ytr = gt.merge_yatir_fluxes_landuse(
    fname_ctl='./ctl_d03_VWCx2_postprocessed.nc',
    fname_yatir='./ytr_d03_VWCx2_postprocessed.nc')

ds_diff = xr.concat([ctlday, ytrday, ctl_minus_ytr],
                    dim=pd.Index(['yatir dry',
                                  'yatir wet',
                                  'Yatir dry - Yatir wet'],
                                 name='WRFrun'))

# make bottom_top_stag, bottom_top into coordinate variables
ds_diff = ds_diff.assign_coords({'bottom_top_stag':
                                 np.arange(ds_diff.dims['bottom_top_stag'])})
ds_diff = ds_diff.assign_coords({'bottom_top':
                                 np.arange(ds_diff.dims['bottom_top'])})
# set 'long_name' attribute to match description
ds = gt.set_attributes_for_plotting(ds_diff)

yatir_idx = 21  # list(ds_diff['PFT'].values).index('Yatir')
#ds_diff = ds_diff.assign(yatir_mask=ds_diff.sel(WRFrun='yatir dry')['LU_INDEX'] == yatir_idx)


def three_panel_quadmesh_compare_vertical_var(varname, cmap='RdBu'):
    """three-panel WRF variable comparison with sliders for z, time

    Create a three-panel plot showing values for W vertical wind
    velocity (W) with sliders to select vertical level and time stamp.

    Display a contour plot to show height above ground of the
    currently displayed vertical level.

    The three panels show values for the control run, Yatir run, and
    control - yatir difference.

    """

    hour_select = pn.widgets.IntSlider(start=0, end=23, value=13, name='Hour',
                                       orientation='vertical',
                                       direction='rtl')
    var_varies_vertically = len(gt.get_vdim(ds, varname)) > 0

    vdim = gt.get_vdim(ds, varname)

    if 'stag' in vdim:
        agl_var = 'height_agl_stag'
        zmax = ds[vdim].size
    elif vdim == []:   # this variable does not vary vertically
        zmax = 0
    else:
        agl_var = 'height_agl'
        zmax = ds[vdim].size

    z_select = pn.widgets.IntSlider(start=0, end=zmax, value=1,
                                    name='vertical level',
                                    orientation='vertical',
                                    direction='rtl',
                                    disabled=(var_varies_vertically is False))

    # bounds for the figures in fraction of the panel,
    fig_bounds = (0.2, 0.2, 0.8, 0.8)

    @pn.depends(hour_select, z_select)
    def get_contour_agl(hour_select, z_select):
        """create contours of height above ground level
        """
        # zstag: height of staggered Z levels, calucated by wrf-python
        # ter: height of terrain (meters above sea level)
        # calculate staggered Z level height above ground level (agl)
        agl_contour = ds[agl_var].sel({'WRFrun': 'yatir dry',
                                       'hour': hour_select,
                                       vdim: z_select}).hvplot.contour(
                                           x='XLONG',
                                           y='XLAT',
                                           z=agl_var,
                                           title='WRF height AGL').opts(
                                               frame_width=200,
                                               frame_height=200)
        return(agl_contour)

    @pn.depends(hour_select, z_select)
    def get_quadmesh_control(hour_select, z_select):
        """
        """
        # if var_varies_vertically:
        #     idx = {'WRFrun': 'control',
        #            'hour': hour_select,
        #            vdim: z_select}
        # else:
        #     idx = {'WRFrun': 'control',
        #            'hour': hour_select}
        vdim = gt.get_vdim(ds, varname)
        vmin, vmax = gt.get_min_max(ds, varname, hour_select, z_select)
        sys.stdout.write('hour_select: {}\n'.format(hour_select))
        sys.stdout.write('z_select: {}\n'.format(z_select))
        sys.stdout.write('varname: {}\n'.format(varname))
        sys.stdout.flush()
        qm = ds[varname].sel({'WRFrun': 'yatir dry',
                              'hour': hour_select,
                              vdim: z_select}).hvplot.quadmesh(
                                  x='XLONG',
                                  y='XLAT',
                                  z=varname,
                                  title='Yatir dry',
                                  clim=(vmin, vmax),
                                  cmap=cmap).opts(frame_width=200,
                                                  frame_height=200)
        return(qm)

    @pn.depends(hour_select, z_select)
    def get_quadmesh_yatir(hour_select, z_select):
        """
        """
        vdim = gt.get_vdim(ds, varname)
        vmin, vmax = gt.get_min_max(ds, varname, hour_select, z_select)
        qm = ds[varname].sel({'WRFrun': 'yatir wet',
                              'hour': hour_select,
                              vdim: z_select}).hvplot.quadmesh(
                                  x='XLONG',
                                  y='XLAT',
                                  z=varname,
                                  title='Yatir wet',
                                  cmap=cmap,
                                  clim=(vmin, vmax)).opts(frame_width=200,
                                                          frame_height=200)
        return(qm)

    @pn.depends(hour_select, z_select)
    def get_quadmesh_diff(hour_select, z_select):
        """
        """
        vdim = gt.get_vdim(ds, varname)
        vmin, vmax = gt.get_min_max(ds, varname, hour_select, z_select)
        qm = ds[varname].sel({'WRFrun': 'Yatir dry - Yatir wet',
                              'hour': hour_select,
                              vdim: z_select}).hvplot.quadmesh(
                                  x='XLONG',
                                  y='XLAT',
                                  z=varname,
                                  #clim=(vmin, vmax),
                                  symmetric=True,
                                  cmap='RdBu',
                                  title='Yatir dry - Yatir wet').opts(
                                      frame_width=200,
                                      frame_height=200)
        return(qm)

    #main_title = '## ' + ds[varname].long_name
    main_title = '## ' + varname

    the_plot = pn.Column(pn.Row(pn.pane.Markdown(main_title)),
                         pn.Row(get_quadmesh_control, get_quadmesh_yatir,
                                hour_select, z_select),
                         pn.Row(get_quadmesh_diff, get_contour_agl))
    the_plot_servable = the_plot.servable()
    return(the_plot_servable)


def three_panel_quadmesh_compare_surface_var(varname, cmap='RdBu'):
    """three-panel WRF variable comparison with slider for time

    Create a three-panel plot showing values for a WRF variable) with
    one slider to select time stamp.
    The three panels show values for the control run, Yatir run, and
    control - yatir difference.

    """

    hour_select = pn.widgets.IntSlider(start=0, end=23, value=13, name='Hour',
                                       orientation='vertical',
                                       direction='rtl')
    z_select = None  # this is a surface variable
    # bounds for the figures in fraction of the panel,
    fig_bounds = (0.2, 0.2, 0.8, 0.8)

    @pn.depends(hour_select)
    def get_quadmesh_control(hour_select):
        """
        """
        vmin, vmax = gt.get_min_max(ds, varname, hour_select, z_select)
        qm = ds[varname].sel({'WRFrun': 'yatir dry',
                              'hour': hour_select}).hvplot.quadmesh(
                                  x='XLONG',
                                  y='XLAT',
                                  z=varname,
                                  title='Yatir Dry',
                                  clim=(vmin, vmax),
                                  cmap=cmap).opts(frame_width=200,
                                                  frame_height=200)
        return(qm)

    @pn.depends(hour_select)
    def get_quadmesh_yatir(hour_select):
        """
        """
        vmin, vmax = gt.get_min_max(ds, varname, hour_select, z_select)
        qm = ds[varname].sel({'WRFrun': 'yatir wet',
                              'hour': hour_select}).hvplot.quadmesh(
                                  x='XLONG',
                                  y='XLAT',
                                  z=varname,
                                  title='Yatir wet',
                                  cmap=cmap,
                                  clim=(vmin, vmax)).opts(frame_width=200,
                                                          frame_height=200)
        return(qm)

    @pn.depends(hour_select)
    def get_quadmesh_diff(hour_select):
        """
        """
        vmin, vmax = gt.get_min_max(ds, varname, hour_select, z_select)
        qm = ds[varname].sel({'WRFrun': 'Yatir dry - Yatir wet',
                              'hour': hour_select}).hvplot.quadmesh(
                                  x='XLONG',
                                  y='XLAT',
                                  z=varname,
                                  #clim=(vmin, vmax),
                                  symmetric=True,
                                  cmap='RdBu',
                                  title='Yatir dry - Yatir wet').opts(
                                      frame_width=200,
                                      frame_height=200)
        return(qm)

    # main_title = '## ' + ds[varname].long_name
    main_title = '## ' + varname
    the_plot = pn.Column(pn.Row(pn.pane.Markdown(main_title)),
                         pn.Row(get_quadmesh_control, get_quadmesh_yatir,
                                hour_select),
                         pn.Row(get_quadmesh_diff))
    the_plot_servable = the_plot.servable()
    sys.stdout.write('saving representation of the_plot for {} to disk\n'.format(varname))
    sys.stdout.flush()
    import bokeh
    #the_plot_json = bokeh.serialize_json(the_plot.get_root())
    return(the_plot)
