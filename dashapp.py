import dash
from dash import dcc, html, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
import base64
import os

# Initialize Dash App
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Minimalist Style Settings
def minimalist_style():
    return {
        'padding': '10px',
        'margin': 'auto',
        'maxWidth': '600px',
        'fontFamily': 'Arial, sans-serif'
    }

# Layout
app.layout = html.Div([
    html.H1("Document Processing Portal", style={
        'textAlign': 'center', 'marginBottom': '20px', 'fontWeight': 'bold', 'color': '#2C3E50', 'fontSize': '2.5em'}),

    # Drag-and-Drop Area
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

    # Configuration Options
    html.Div([
        # Rename Option
        html.Div([
            html.Label("Rename Based on Entity:", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
            dcc.Dropdown(
                id='entity-dropdown',
                options=[
                    {'label': 'PO Number', 'value': 'po_number'},
                    {'label': 'Invoice Number', 'value': 'invoice_number'},
                    {'label': 'Custom Entity', 'value': 'custom'}
                ],
                placeholder="Select an entity",
                style={'marginBottom': '15px', 'borderRadius': '5px'}
            ),
        ]),

        # Summarization Option
        html.Div([
            dbc.Checklist(
                options=[{"label": "Summarize Document", "value": "summarize"}],
                value=[],
                id="summarize-checklist",
                switch=True,
                style={'marginBottom': '15px'}
            ),
        ]),

        # Masking Option
        html.Div([
            dbc.Checklist(
                options=[{"label": "Mask PII", "value": "mask"}],
                value=[],
                id="masking-checklist",
                switch=True
            ),
        ]),
    ], style={**minimalist_style(), 'backgroundColor': '#F8F9FA', 'padding': '20px', 'borderRadius': '10px', 'boxShadow': '0 2px 5px rgba(0, 0, 0, 0.1)'}),

    # Submit Button
    html.Div([
        dbc.Button("Process Documents", id="process-btn", color="primary", n_clicks=0, 
                   style={"width": "100%", "marginTop": "20px", 'fontSize': '1.2em', 'fontWeight': 'bold'})
    ]),

    # Output Section
    html.Div(id='output-div', style={'marginTop': '30px'}),

], style={**minimalist_style(), 'backgroundColor': '#F5F5F5', 'padding': '30px', 'borderRadius': '10px'})


# Callbacks
@app.callback(
    Output('output-div', 'children'),
    Input('process-btn', 'n_clicks'),
    State('upload-pdf', 'contents'),
    State('entity-dropdown', 'value'),
    State('summarize-checklist', 'value'),
    State('masking-checklist', 'value')
)
def process_documents(n_clicks, contents, entity, summarize, mask):
    if n_clicks > 0:
        if not contents:
            return "No files uploaded. Please upload PDF files."

        output = []
        for content in contents:
            # Decode the uploaded PDF file
            content_type, content_string = content.split(',')
            decoded = base64.b64decode(content_string)
            
            # Placeholder: Save file locally (optional)
            with open(f"temp_file.pdf", "wb") as f:
                f.write(decoded)

            # Placeholder: Logic for renaming, summarizing, and masking
            rename_text = f"Renamed based on: {entity}" if entity else "No renaming applied."
            summarize_text = "Document summarized." if "summarize" in summarize else "No summarization applied."
            masking_text = "PII masked." if "mask" in mask else "No masking applied."

            output.append(html.Div([
                html.P(rename_text, style={'fontSize': '1em', 'color': '#2C3E50'}),
                html.P(summarize_text, style={'fontSize': '1em', 'color': '#2C3E50'}),
                html.P(masking_text, style={'fontSize': '1em', 'color': '#2C3E50'}),
                html.Hr()
            ]))

        return output


if __name__ == '__main__':
    app.run_server(host="0.0.0.0",debug=True)
