import panel as pn

import time
import sys

from rq import Queue
from worker import conn
import surface_panels_quick_dirty as spqd


def get_intro_pgraph():
    return(pn.pane.Markdown('''# Yatir Parameterizaton WRF results

A collection of plots showing WRF-simulated surface energy and carbon
fluxes for two different simulations of [Yatir
Forest](https://www.weizmann.ac.il/EPS/Yakir/research-activities/field-research/yatir-forest-location-and-background)
in Israel.  Both WRF runs set a 15-km radius surrounding Yatir Forest
to a lower albedo and higher surface roughness length relative to an
'out of the box' WRF run (in which the area is occupied by
MODIS-derived shrubland and desert).  The 'wet' run 'irrigates' the
forest by doubling the volumetric water content from the dry run (not
exceeding 100%, of course).  ''').get_root())

# # farm out the plotting to worker processes because > 3 times out on Heroku.
# q = Queue(connection=conn)

# plot_W = q.enqueue(spqd.three_panel_quadmesh_compare_vertical_var,
#                    args=('W', 'PRGn'),
#                    job_id='W_plot_job')
# plot_theta = q.enqueue(spqd.three_panel_quadmesh_compare_surface_var,
#                        args=('HFX', 'Reds'),
#                        job_id='HFX_plot_job')
# plot_LH = q.enqueue(spqd.three_panel_quadmesh_compare_surface_var,
#                     args=('LH', 'Blues'),
#                     job_id='LH_plot_job')

# result_lh = plot_LH.fetch('LH_plot_job', connection=conn).result
# while result_lh is None:
#     sys.stdout.write('LH not yet finished')
#     sys.stdout.flush()
#     time.sleep(2)
#     result_lh = plot_LH.fetch('LH_plot_job', connection=conn).result

# nprint = 0
# while nprint < 5:
#     sys.stdout.write('LH job type ' + str(type(result_lh)))
#     sys.stdout.write('\n')
#     sys.stdout.write('LH job ~' + str(result_lh) + '~')
#     sys.stdout.write('\n')
#     sys.stdout.flush()
#     nprint = nprint + 1

# time.sleep(10)

# pn.pane.Markdown('''#After the delay
# print this stuff after the delay
# ''').servable()
