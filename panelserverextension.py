"""make the Yatir visualization available to mybinder as a dashboard app

adapted from https://github.com/pyviz-demos/clifford
"""


from subprocess import Popen

def load_jupyter_server_extension(nbapp):
    """serve the Yatir viz ipynb directory with bokeh server"""
    Popen(["panel", "serve", "yatir_visualization.ipynb", "--allow-websocket-origin=*"])
