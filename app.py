"""a toy app demonstrating Bokeh and Flask

based on https://blog.thedataincubator.com/2015/09/painlessly-deploying-data-apps-with-bokeh-flask-and-heroku/
"""

import sys
import time
from flask import Flask, render_template
from yatir_visualization import get_intro_pgraph
from surface_panels_quick_dirty import three_panel_quadmesh_compare_surface_var
from bokeh.embed import components
app = Flask(__name__)


@app.route('/hello_page')
def hello_world():
    # this is a comment, just like in Python
    # note that the function name and the route argument
    # do not need to be the same.
    return 'Hello World!'


@app.route('/index')
def index():
    """index.html has to be in a 'templates' subdirectory

    https://stackoverflow.com/questions/37465506/jinja2-exceptions-templatenotfound
    """
    sys.stdout.write('hello from index\n')
    sys.stdout.flush()
    script = None
    while script is None:
        #time.sleep(31)
        LH_plot = three_panel_quadmesh_compare_surface_var('LH', 'Blues')
        sys.stdout.write('LH_plot: {}/n'.format(type(LH_plot.get_root())))
        sys.stdout.flush()
        script_LH, div_LH = components(LH_plot.get_root())
        script_intro, div_intro = components(get_intro_pgraph())
        script_LH_plot, div_LH_plot = components(get_intro_pgraph())
        return(render_template('index.html',
                               script_intro=script_intro,
                               script_LH_plot=script_LH_plot,
                               div_intro=div_intro,
                               div_LH_plot=div_LH_plot))


if __name__ == '__main__':
    sys.stdout.write('hello from main\n')
    sys.stdout.flush()
    app.run(port=33507)   # run through heroku.  heroku reserves port
                          # 33507 for flask
    # app.run(debug=True) #run locally through flask
