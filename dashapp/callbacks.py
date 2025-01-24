from dash import Input, Output, State, callback_context, html, ALL
import os
import base64
import logging
from ast import literal_eval
from src.processing.pdf_processor import process_pdf


def generate_file_list(files):
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
                    'marginLeft': 'auto',
                },
            ),
        ],
            style={
                'display': 'flex',
                'justifyContent': 'space-between',
                'alignItems': 'center',
                'marginBottom': '5px',
            }) for idx, file in enumerate(files)
    ]


def register_callbacks(app):
    @app.callback(
        [Output('file-list', 'children'),
         Output('error-message', 'children'),
         Output('uploaded-files-store', 'data'),
         Output('output-div', 'children'),
         Output('processing-message', 'children')],
        [Input('upload-pdf', 'filename'),
         Input('upload-pdf', 'contents'),
         Input({'type': 'delete-button', 'index': ALL}, 'n_clicks'),
         Input('process-btn', 'n_clicks')],
        [State('uploaded-files-store', 'data')],
        prevent_initial_call=True,
    )
    def handle_callbacks(new_filenames, new_contents, delete_clicks, process_clicks, stored_files):
        stored_files = stored_files or []
        error_message = ""
        output_div = ""
        processing_message = ""

        ctx = callback_context
        triggered_id = ctx.triggered_id

        if isinstance(triggered_id, dict) and triggered_id.get('type') == 'delete-button':
            index_to_delete = triggered_id['index']
            if delete_clicks[index_to_delete]:
                stored_files.pop(index_to_delete)
            return generate_file_list(stored_files), "", stored_files, output_div, processing_message

        if triggered_id == 'upload-pdf':
            if new_filenames and new_contents:
                for filename, content in zip(new_filenames, new_contents):
                    if len(stored_files) < 10:
                        if filename.lower().endswith('.pdf') and filename not in [file['filename'] for file in stored_files]:
                            stored_files.append({'filename': filename, 'content': content})
                    else:
                        error_message = "Maximum files allowed exceeded."
                        break
            return generate_file_list(stored_files), error_message, stored_files, output_div, processing_message

        if triggered_id == 'process-btn':
            if not stored_files:
                output_div = html.Div("No files to process.")
                return generate_file_list(stored_files), error_message, stored_files, output_div, processing_message

            output = []
            temp_dir = "temp_uploads"
            os.makedirs(temp_dir, exist_ok=True)

            processing_message = "Processing documents, please wait..."

            for file in stored_files:
                try:
                    temp_path = os.path.join(temp_dir, file['filename'])

                    prefix = 'data:application/pdf;base64,'
                    base64_content = file['content'].split(prefix)[-1] if prefix in file['content'] else file['content']

                    clean_content = base64_content.replace('\n', '').replace(' ', '')
                    clean_content += '=' * ((4 - len(clean_content) % 4) % 4)

                    pdf_bytes = base64.b64decode(clean_content)

                    with open(temp_path, "wb") as f:
                        f.write(pdf_bytes)

                    result = process_pdf(temp_path)
                    output.append(html.Div([
                        html.P(f"File: {file['filename']} processed successfully."),
                    ]))
                except Exception as e:
                    output.append(html.Div([
                        html.P(f"Error processing {file['filename']}: {str(e)}"),
                        html.Hr()
                    ]))
                    logging.error(f"PDF processing error for {file['filename']}: {str(e)}")

            return [], "", [], output, ""

        return generate_file_list(stored_files), error_message, stored_files, output_div, processing_message
