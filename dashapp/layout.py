from dash import dcc, html
import dash_bootstrap_components as dbc
import yaml
import os

try:
    with open("config.yml", "r") as config_file:
        config = yaml.safe_load(config_file)
except FileNotFoundError:
    config = {"style": {}, "app": {}}
    print("Warning: config.yml not found. Using default configuration.")

minimalist_style = {
    'padding': config['style'].get('padding', '10px'),
    'margin': config['style'].get('margin', 'auto'),
    'maxWidth': f"{config['style'].get('max_width', '600')}px",
    'fontFamily': config['style'].get('font_family', 'Arial, sans-serif')
}

upload_style = {
    'width': '100%',
    'height': f"{config['style'].get('upload_height', '120')}px",
    'lineHeight': f"{config['style'].get('upload_height', '120')}px",
    'borderWidth': '2px',
    'borderStyle': 'dashed',
    'borderRadius': '10px',
    'textAlign': 'center',
    'marginBottom': '20px',
    'backgroundColor': config['style'].get('upload_border_color', '#ECF0F1')
}

header_style = {
    'textAlign': 'center',
    'marginBottom': '20px',
    'fontWeight': 'bold',
    'color': config['style'].get('header_text_color', '#2C3E50'),
    'fontSize': '2.5em'
}

hr_options = [
    {'label': 'HR - Employee ID', 'value': 'hr_employee_id'},
    {'label': 'HR - SOP ID', 'value': 'hr_sop_id'}
]
finance_options = [
    {'label': 'Finance - PO Number', 'value': 'finance_po_number'},
    {'label': 'Finance - Contract Number', 'value': 'finance_contract_number'}
]
operation_options = [
    {'label': 'Operation - Batch Number', 'value': 'operation_batch_number'},
    {'label': 'Operation - Serial Number', 'value': 'operation_serial_number'}
]

app_layout = html.Div([
    html.H1("Document Processing Portal", style=header_style),
    dcc.Store(id='uploaded-files-store', storage_type='memory'),  
    dcc.Upload(
        id='upload-pdf',
        children=html.Div([
            html.I(className="fas fa-cloud-upload-alt", style={'fontSize': '24px', 'marginRight': '10px'}),
            html.Span('Drag and Drop or '),
            html.A('Select PDF Files', style={'color': '#3498DB', 'textDecoration': 'underline'})
        ]),
        style=upload_style,
        multiple=True
    ),

    html.Div([
        html.Label("Uploaded Files:", style={'fontWeight': 'bold', 'marginBottom': '10px'}),
        html.Ul(id='file-list', style={
            'backgroundColor': '#F8F9FA',
            'padding': '10px',
            'borderRadius': '5px',
            'listStyleType': 'none',
            'boxShadow': '0 2px 5px rgba(0, 0, 0, 0.1)'
        })
    ], style={'marginBottom': '20px'}),

    html.Div([
        html.Div([
            html.Label("Rename Based on Entity (HR):", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
            dcc.Dropdown(
                id='hr-entity-dropdown',
                options=hr_options,
                placeholder="Select an HR entity",
                style={'marginBottom': '15px', 'borderRadius': '5px'}
            ),
        ]),
        html.Div([
            html.Label("Rename Based on Entity (Finance):", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
            dcc.Dropdown(
                id='finance-entity-dropdown',
                options=finance_options,
                placeholder="Select a Finance entity",
                style={'marginBottom': '15px', 'borderRadius': '5px'}
            ),
        ]),
        html.Div([
            html.Label("Rename Based on Entity (Operation):", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
            dcc.Dropdown(
                id='operation-entity-dropdown',
                options=operation_options,
                placeholder="Select an Operation entity",
                style={'marginBottom': '15px', 'borderRadius': '5px'}
            ),
        ]),

        html.Div([
            dbc.Checklist(
                options=[{"label": "Summarize Document", "value": "summarize"}],
                value=[],
                id="summarize-checklist",
                switch=True,
                style={'marginBottom': '15px'}
            ),
        ]),
        html.Div([
            dbc.Checklist(
                options=[{"label": "Mask PII", "value": "mask"}],
                value=[],
                id="masking-checklist",
                switch=True
            ),
        ]),
    ], style={
        **minimalist_style,
        'backgroundColor': '#F8F9FA',
        'padding': '20px',
        'borderRadius': '10px',
        'boxShadow': '0 2px 5px rgba(0, 0, 0, 0.1)'
    }),

    html.Div([
        dbc.Button(
            "Process Documents",
            id="process-btn",
            color="primary",
            n_clicks=0,
            style={"width": "100%", "marginTop": "20px", 'fontSize': '1.2em', 'fontWeight': 'bold'}
        )
    ]),

    html.Div(id='output-div', style={'marginTop': '30px'}),
    html.Div(id='error-message', style={'color': 'red', 'fontWeight': 'bold', 'marginTop': '10px'}),
    html.Div(id='processing-message', style={'color': 'blue', 'fontWeight': 'bold', 'marginTop': '20px', 'textAlign': 'center'}),
], style={**minimalist_style, 'backgroundColor': '#F5F5F5', 'padding': '30px', 'borderRadius': '10px'})
