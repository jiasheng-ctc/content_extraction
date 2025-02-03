from dash import Dash
import dash_bootstrap_components as dbc
from dashapp.layout import app_layout
from dashapp.callbacks import register_callbacks
import yaml

with open("config.yml", "r") as config_file:
    config = yaml.safe_load(config_file)

external_stylesheet = [dbc.themes.BOOTSTRAP] if config['app'].get('external_stylesheet') == 'bootstrap' else []
host = config['app'].get('host', '0.0.0.0')
port = config['app'].get('port', 8050)

app = Dash(__name__, external_stylesheets=external_stylesheet)
app.title = 'GenAI - Content Extraction Demo'
server = app.server

app.layout = app_layout

register_callbacks(app)

if __name__ == '__main__':
    app.run_server(debug=True, host=host, port=port)
