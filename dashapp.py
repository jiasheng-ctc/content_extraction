import dash
from dash import dcc, html, Input, Output, State, callback_context, ALL
import dash_bootstrap_components as dbc
import base64
import re


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

def minimalist_style():
    return {
        'padding': '10px',
        'margin': 'auto',
        'maxWidth': '600px',
        'fontFamily': 'Arial, sans-serif'
    }

app.layout = html.Div([
    html.H1("Document Processing Portal", style={
        'textAlign': 'center', 'marginBottom': '20px', 'fontWeight': 'bold', 'color': '#2C3E50', 'fontSize': '2.5em'}),

    dcc.Upload(
        id='upload-pdf',
        children=html.Div([
            html.I(className="fas fa-cloud-upload-alt", style={'fontSize': '24px', 'marginRight': '10px'}),
            html.Span('Drag and Drop or '),
            html.A('Select PDF Files', style={'color': '#3498DB', 'textDecoration': 'underline'})
        ]),
        style={
            'width': '100%',
            'height': '120px',
            'lineHeight': '120px',
            'borderWidth': '2px',
            'borderStyle': 'dashed',
            'borderRadius': '10px',
            'textAlign': 'center',
            'marginBottom': '20px',
            'backgroundColor': '#ECF0F1'
        },
        multiple=True
    ),

    html.Div([
        html.Label("Uploaded Files:", style={'fontWeight': 'bold', 'marginBottom': '10px'}),
        html.Ul(id='file-list', style={'backgroundColor': '#F8F9FA', 'padding': '10px', 'borderRadius': '5px', 'listStyleType': 'none', 'boxShadow': '0 2px 5px rgba(0, 0, 0, 0.1)'})
    ], style={'marginBottom': '20px'}),

    html.Div([
        html.Div([
            html.Label("Rename Based on Entity (HR):", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
            dcc.Dropdown(
                id='hr-entity-dropdown',
                options=[
                    {'label': 'HR - Employee ID', 'value': 'hr_employee_id'},
                    {'label': 'HR - Payroll ID', 'value': 'hr_payroll_id'}
                ],
                placeholder="Select an HR entity",
                style={'marginBottom': '15px', 'borderRadius': '5px'}
            ),
        ]),

        html.Div([
            html.Label("Rename Based on Entity (Finance):", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
            dcc.Dropdown(
                id='finance-entity-dropdown',
                options=[
                    {'label': 'Finance - PO Number', 'value': 'finance_po_number'},
                    {'label': 'Finance - Invoice Number', 'value': 'finance_invoice_number'}
                ],
                placeholder="Select a Finance entity",
                style={'marginBottom': '15px', 'borderRadius': '5px'}
            ),
        ]),

        html.Div([
            html.Label("Rename Based on Entity (Manufacturing):", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
            dcc.Dropdown(
                id='manufacturing-entity-dropdown',
                options=[
                    {'label': 'Manufacturing - Batch Number', 'value': 'manufacturing_batch_number'},
                    {'label': 'Manufacturing - Serial Number', 'value': 'manufacturing_serial_number'}
                ],
                placeholder="Select a Manufacturing entity",
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
    ], style={**minimalist_style(), 'backgroundColor': '#F8F9FA', 'padding': '20px', 'borderRadius': '10px', 'boxShadow': '0 2px 5px rgba(0, 0, 0, 0.1)'}),

    html.Div([
        dbc.Button("Process Documents", id="process-btn", color="primary", n_clicks=0, 
                   style={"width": "100%", "marginTop": "20px", 'fontSize': '1.2em', 'fontWeight': 'bold'})
    ]),

    html.Div(id='output-div', style={'marginTop': '30px'}),

    html.Div(id='error-message', style={'color': 'red', 'fontWeight': 'bold', 'marginTop': '10px'}),
], style={**minimalist_style(), 'backgroundColor': '#F5F5F5', 'padding': '30px', 'borderRadius': '10px'})

uploaded_files = []

def generate_file_list():
    return [
        html.Li([
            html.Span(file['filename'], style={'marginRight': '10px'}),
            html.Span(
                "✖", 
                id={'type': 'delete-button', 'index': idx}, 
                style={
                    'cursor': 'pointer', 
                    'color': 'red', 
                    'fontWeight': 'bold', 
                    'marginLeft': 'auto'
                }
            )
        ], style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center', 'marginBottom': '5px', 'color': '#2C3E50'})
        for idx, file in enumerate(uploaded_files)
    ]

@app.callback(
    [Output('file-list', 'children'), Output('error-message', 'children')],
    [Input('upload-pdf', 'filename'), Input('upload-pdf', 'contents'), Input({'type': 'delete-button', 'index': ALL}, 'n_clicks')],
    prevent_initial_call=True
)
def update_file_list(new_filenames, new_contents, delete_clicks):
    global uploaded_files
    error_message = ""

    ctx = callback_context
    if ctx.triggered and 'delete-button' in ctx.triggered[0]['prop_id']:
        triggered_button = eval(ctx.triggered[0]['prop_id'].split('.')[0])
        index_to_delete = triggered_button['index']
        if delete_clicks[index_to_delete]:
            uploaded_files.pop(index_to_delete)
        return generate_file_list(), ""

    if new_filenames and new_contents:
        total_files = len(uploaded_files) + len(new_filenames)
        if total_files > 10:
            num_to_add = 10 - len(uploaded_files)
            for filename, content in zip(new_filenames[:num_to_add], new_contents[:num_to_add]):
                if filename not in [file['filename'] for file in uploaded_files]:
                    uploaded_files.append({'filename': filename, 'content': content})
            error_message = "Error: Maximum of 10 documents allowed. Some files were not uploaded."
            return generate_file_list(), error_message

        for filename, content in zip(new_filenames, new_contents):
            if filename not in [file['filename'] for file in uploaded_files]:
                uploaded_files.append({'filename': filename, 'content': content})

    return generate_file_list(), error_message

@app.callback(
    Output('output-div', 'children'),
    Input('process-btn', 'n_clicks'),
    State('summarize-checklist', 'value'),
    State('masking-checklist', 'value'),
    State('hr-entity-dropdown', 'value'),
    State('finance-entity-dropdown', 'value'),
    State('manufacturing-entity-dropdown', 'value')
)
def process_documents(n_clicks, summarize, mask, hr_entity, finance_entity, manufacturing_entity):
    global uploaded_files

    if n_clicks > 0:
        if not uploaded_files:
            return "No files uploaded. Please upload PDF files."

        output = []
        for file in uploaded_files:
            file_name = file['filename']
            rename_info = f"Renamed using: {hr_entity or finance_entity or manufacturing_entity}" if any([hr_entity, finance_entity, manufacturing_entity]) else "No renaming applied."
            summarize_info = "Summarization applied." if "summarize" in summarize else "No summarization applied."
            mask_info = "PII masking applied." if "mask" in mask else "No PII masking applied."

            output.append(html.Div([
                html.P(f"File: {file_name}"),
                html.P(rename_info),
                html.P(summarize_info),
                html.P(mask_info),
                html.Hr()
            ]))

        return output

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)
