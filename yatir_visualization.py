import numpy as np
import xarray as xr
import panel as pn
import pandas as pd

from rq import Queue
from worker import conn
import surface_panels_quick_dirty as spqd
import geoviews_tools as gt

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
ds_diff = gt.set_attributes_for_plotting(ds_diff)

yatir_idx = 21  # list(ds_diff['PFT'].values).index('Yatir')
#ds_diff = ds_diff.assign(yatir_mask=ds_diff.sel(WRFrun='yatir dry')['LU_INDEX'] == yatir_idx)


pn.pane.Markdown('''# Yatir Parameterizaton WRF results

A collection of plots showing WRF-simulated surface energy and carbon
fluxes for two different simulations of [Yatir
Forest](https://www.weizmann.ac.il/EPS/Yakir/research-activities/field-research/yatir-forest-location-and-background)
in Israel.  Both WRF runs set a 15-km radius surrounding Yatir Forest
to a lower albedo and higher surface roughness length relative to an
'out of the box' WRF run (in which the area is occupied by
MODIS-derived shrubland and desert).  The 'wet' run 'irrigates' the
forest by doubling the volumetric water content from the dry run (not
exceeding 100%, of course).  ''').servable()

# farm out the plotting to worker processes because > 3 times out on Heroku.
q = Queue(connection=conn)

plot_W = q.enqueue(spqd.three_panel_quadmesh_compare_vertical_var,
                   ds_diff, 'W', cmap='PRGn')
plot_theta = q.enqueue(spqd.three_panel_quadmesh_compare_vertical_var,
                       ds_diff, 'LH', cmap='Reds')
plot_LH = q.enqueue(spqd.three_panel_quadmesh_compare_vertical_var,
                    ds_diff, 'LH', cmap='Blues')
