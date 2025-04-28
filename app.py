import os
import sys
from flask import Flask
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
from dash_extensions import Mermaid
import time
from dash.exceptions import PreventUpdate
from dash import callback_context
 
# Ensure correct import paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'MACROS')))
from main import processChat, getJIRAWorkflowGraph
from MerMaid.mermaid import generate_mermaid_diagram
 
# Initialize Flask server
server = Flask(__name__)
 
# Create a Dash app bound to Flask
app = dash.Dash(__name__, server=server, suppress_callback_exceptions=True)
 
# Initialize global variables for the chat
jira_graph = getJIRAWorkflowGraph()
chat_history = []
PORT = 5000
 
# Define the layout of the Dash app
app.layout = html.Div(
    [
        html.Div(
            style={
                "position": "fixed",
                "top": 0,
                "left": 0,
                "right": 0,
                "bottom": 0,
                # "backgroundImage": "url('/static/back_ai.jpg')",
                "backgroundColor": "blue",
                "zIndex": "-1"
            }
        ),
        html.Header(
            html.H1("JIRA ASSISTANT CHATBOT", style={"margin": "0", "color": "#FFFFFF"}),
            style={
                "backgroundColor": "#003366",
                "padding": "15px",
                "textAlign": "center",
                "boxShadow": "0 4px 8px rgba(0, 0, 0, 0.2)",
                "borderBottom": "2px solid #001f3f"
            }
        ),
        html.Div(
            [
                # Chat Input and Response Area
                html.Div(
                    style={
                        "display": "flex",
                        "justifyContent": "center",
                        "alignItems": "center",
                        "gap": "20px",
                        "marginBottom": "25px"
                    },
                    children=[
                        dcc.Textarea(
                            id="input-box",
                            placeholder="Type your query about JIRA workflow...",
                            style={
                                "flex": "1",
                                "minHeight": "80px",
                                "padding": "12px",
                                "fontSize": "16px",
                                "borderRadius": "8px",
                                "border": "1px solid #7aa0c4",  
                                "backgroundColor": "#0A2A43",
                                "color": "#FFFFFF",
                                "resize": "vertical"
                            }
                        ),
                        dcc.Textarea(
                            id="response-box",
                            placeholder="Assistant's response will appear here...",
                            style={
                                "flex": "1",
                                "minHeight": "80px",
                                "padding": "12px",
                                "fontSize": "16px",
                                "borderRadius": "8px",
                                "border": "1px solid #7aa0c4",
                                "backgroundColor": "#0A2A43",
                                "color": "#FFFFFF",
                                "resize": "vertical",
                                "overflowY": "auto",
                            },
                            readOnly=True
                        ),
                    ],
                ),
                html.Button(
                    "Send",
                    id="send-button",
                    n_clicks=0,
                    style={
                        "marginTop": "15px",
                        "padding": "12px 24px",
                        "backgroundColor": "#1A73E8",
                        "color": "#FFFFFF",
                        "border": "none",
                        "borderRadius": "5px",
                        "cursor": "pointer",
                        "fontSize": "16px",
                        "boxShadow": "0 2px 4px rgba(0, 0, 0, 0.2)"
                    }
                ),
            ],
            style={"textAlign": "center"}
        ),
        html.Div(
            [
                html.Button("👍", id="thumbs-up", n_clicks=0, style={
                    "marginTop": "10px",
                    "padding": "10px",
                    "backgroundColor": "#4CAF50",
                    "color": "#FFFFFF",
                    "border": "none",
                    "borderRadius": "50%",
                    "cursor": "pointer",
                    "fontSize": "20px",
                    "marginRight": "10px",
                }, title="Like"),
                html.Button("👎", id="thumbs-down", n_clicks=0, style={
                    "marginTop": "10px",
                    "padding": "10px",
                    "backgroundColor": "#F44336",
                    "color": "#FFFFFF",
                    "border": "none",
                    "borderRadius": "50%",
                    "cursor": "pointer",
                    "fontSize": "20px",
                }, title="Dislike"),
            ],
            style={"display": "flex", "justifyContent": "center", "marginTop": "15px"}
        ),
        html.Div(
            id='feedback-response',
            style={"textAlign": "center", "marginTop": "15px", "color": "#1A73E8", "fontSize": "16px"}
        ),
        # Mind Map and Diagram
        html.Div(
            id='mermaid-container',
            children=[
                html.Div(
                    style={
                        "display": "flex",
                        "justifyContent": "center",  # Center the title
                        "alignItems": "center",
                        "marginBottom": "10px"
                    },
                    children=[
                        html.H2(
                            "Mind Map",
                            style={
                                "textAlign": "center",
                                "color": "#FFFFFF",
                                "fontSize": "20px",
                                "fontWeight": "600"
                            }
                        ),
                        html.Div(
                        [
                            html.Button("➕", id="zoom-in", n_clicks=0, style={
                                "backgroundColor": "#1A73E8", "color": "#FFFFFF", "border": "none",
                                "borderRadius": "50%", "padding": "10px", "margin": "5px",
                                "cursor": "pointer", "fontSize": "20px", "display": "inline-block",
                            }, title="Zoom In"),
                            html.Button("➖", id="zoom-out", n_clicks=0, style={
                                "backgroundColor": "#1A73E8", "color": "#FFFFFF", "border": "none",
                                "borderRadius": "50%", "padding": "10px", "margin": "5px",
                                "cursor": "pointer", "fontSize": "20px", "display": "inline-block",
                            }, title="Zoom Out"),
                        ],
                        style={"display": "flex", "alignItems": "center", "marginLeft": "15px"}  # Add margin here
                    )
                    ]
                ),
                html.Div(
                    id='mermaid-output',
                    style={
                        "border": "2px solid #7aa0c4",
                        "borderRadius": "8px",
                        "padding": "10px",
                        "backgroundColor": "#FFFFFF",
                        "color": "#000000",
                        "overflow": "hidden",
                        "maxHeight": "600px",
                        "textAlign": "center",
                        "position": "relative",
                        "marginTop": "15px",
                    }
                ),
            ],
            style={"position": "relative", "marginTop": "25px", "display": "none"}  # Hide initially
        ),
        dcc.Store(id='zoom-level', data=1.0),
        dcc.Store(id='zoom-position', data={'x': 0, 'y': 0}),
    ],
    style={
        "width": "80%", "maxWidth": "1200px", "margin": "30px auto",
        "padding": "20px", "backgroundColor": "#003366", "borderRadius": "12px",
        "boxShadow": "0 4px 12px rgba(0,0,0,0.2)",
        "fontFamily": "Arial, sans-serif"
    }
)
 
# Define the callback for handling user input and generating responses
@app.callback(
    [Output("response-box", "value"), Output("mermaid-output", "children"), Output("mermaid-container", "style")],
    [Input("send-button", "n_clicks")],
    [State("input-box", "value")],
    prevent_initial_call=True,
)
def update_chat(n_clicks, user_input):
    if not user_input:
        raise PreventUpdate
 
    chat_history.append({"role": "user", "content": user_input})
    formatted_user_input = {"messages": [{"role": "user", "content": user_input}]}
 
    try:
        response = processChat(
            user_input=formatted_user_input,
            chat_history=chat_history,
            compiledGraph=jira_graph
        )
    except Exception as e:
        response = f"Error: {str(e)}"
 
    chat_history.append({"role": "assistant", "content": response})
 
    if response.startswith("Issue ID:"):
        diagram_code = generate_mermaid_diagram(response)
        mermaid_diagram = Mermaid(chart=diagram_code)
        time.sleep(2)
        print("Mind Map Created")
        print(mermaid_diagram)
        return "Mind Map Created", mermaid_diagram, {"display": "block"}
    else:
        return response, None, {"display": "none"}
   
 
# Callback to update the feedback response
@app.callback(
    Output('feedback-response', 'children'),
    [Input('thumbs-up', 'n_clicks'), Input('thumbs-down', 'n_clicks')]
)
def feedback_response(thumbs_up, thumbs_down):
    ctx = callback_context
    if not ctx.triggered:
        return ""
   
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if button_id == 'thumbs-up':
        return "Thank you for your positive feedback!"
    elif button_id == 'thumbs-down':
        return "Thank you for your feedback! We'll improve."
   
#Callback for zoom controls
@app.callback(
    [Output('mermaid-output', 'style'), Output('zoom-level', 'data')],
    [Input('zoom-in', 'n_clicks'), Input('zoom-out', 'n_clicks')],
    [State('zoom-level', 'data')],
    prevent_initial_call=True,
)
def zoom_diagram(zoom_in, zoom_out, current_zoom):
    ctx = dash.callback_context
 
    if not ctx.triggered:
        raise PreventUpdate
 
    triggered_button = ctx.triggered[0]['prop_id'].split('.')[0]
 
    if triggered_button == 'zoom-in':
        current_zoom *= 1.1
    elif triggered_button == 'zoom-out':
        current_zoom *= 0.9
 
    style = {
        'marginTop': '10px',
        'border': '1px solid #ced4da',
        'borderRadius': '5px',
        'padding': '10px',
        'backgroundColor': '#fff',
        'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
        'transform-origin': 'top left',
        'transform': f'scale({current_zoom})'
    }
    return style, current_zoom
    
if __name__ == '__main__':
    server.run(host='0.0.0.0', port=PORT, debug=True)