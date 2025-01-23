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
       [Output('file-list', 'children'), Output('error-message', 'children'), Output('uploaded-files-store', 'data')],
       [Input('upload-pdf', 'filename'), Input('upload-pdf', 'contents'),
        Input({'type': 'delete-button', 'index': ALL}, 'n_clicks')],
       State('uploaded-files-store', 'data'),
       prevent_initial_call=True,
   )
   def update_file_list(new_filenames, new_contents, delete_clicks, stored_files):
       stored_files = stored_files or []
       error_message = ""

       ctx = callback_context
       if ctx.triggered and 'delete-button' in ctx.triggered[0]['prop_id']:
           triggered_button = literal_eval(ctx.triggered[0]['prop_id'].split('.')[0])
           index_to_delete = triggered_button['index']
           if delete_clicks[index_to_delete]:
               stored_files.pop(index_to_delete)
           return generate_file_list(stored_files), "", stored_files

       if new_filenames and new_contents:
           for filename, content in zip(new_filenames, new_contents):
               if len(stored_files) < 10:
                   if filename.lower().endswith('.pdf') and filename not in [file['filename'] for file in stored_files]:
                       stored_files.append({'filename': filename, 'content': content})
               else:
                   error_message = "Maximum files allowed exceeded."
                   break

       return generate_file_list(stored_files), error_message, stored_files

   @app.callback(
       Output('output-div', 'children'),
       Input('process-btn', 'n_clicks'),
       State('uploaded-files-store', 'data'),
       prevent_initial_call=True,
   )
   def process_documents(n_clicks, stored_files):
       if n_clicks > 0 and stored_files:
           output = []
           temp_dir = "temp_uploads"
           os.makedirs(temp_dir, exist_ok=True)

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
                    #    html.P(f"File: {file['filename']} processed."),
                    #    html.P(f"Summary saved at: {result['CSV Path']}"),
                    #    html.Hr()
                   ]))
               except Exception as e:
                   output.append(html.Div([
                       html.P(f"Error processing {file['filename']}: {str(e)}"),
                       html.Hr()
                   ]))
                   logging.error(f"PDF processing error for {file['filename']}: {str(e)}")

           return output