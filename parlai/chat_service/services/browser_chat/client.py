#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import logging
import json
import time
import websocket
import threading
from parlai.core.params import ParlaiParser
from parlai.scripts.interactive_web import WEB_HTML, STYLE_SHEET, FONT_AWESOME
from http.server import BaseHTTPRequestHandler, HTTPServer
import parlai.convai.word_extraction as extraction
from parlai.convai.t5_error_correction import T5_conai

from googletrans import Translator

SHARED = {}

def setup_interactive(ws):
    SHARED['ws'] = ws


new_message = None
message_available = threading.Event()
print("loading Error Correction Model")
model = T5_conai()


class BrowserHandler(BaseHTTPRequestHandler):
    """
    Handle HTTP requests.
    """

    def _interactive_running(self, reply_text):
        data = {}
        print("reply is ", reply_text)
        data['text'] = reply_text.decode('utf-8')
        print("data is ", data)
        if data['text'] == "[DONE]":
            print('[ Closing socket... ]')
            SHARED['ws'].close()
            SHARED['wb'].shutdown()
        json_data = json.dumps(data)
        SHARED['ws'].send(json_data)

    def do_HEAD(self):
        """
        Handle HEAD requests.
        """
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_POST(self):
        """
        Handle POST request, especially replying to a chat message.
        """
        if self.path == '/interact':
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            print("body is", body)
            save_body = body
            self._interactive_running(body)
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            model_response = {'id': 'Model', 'episode_done': False}
            message_available.wait()
            model_response['text'] = new_message
            message_available.clear()
            print("response is ",model_response)
            body_content = save_body.decode('utf-8')
            save_res = model_response['text']
            get_second_res = model_response['text'].split('|')
            if len(get_second_res)==2:
                translator = Translator()
                given_sentence = get_second_res[1]
                print("given sentence is ", given_sentence)
                trans_result = translator.translate(given_sentence, dest="ko")
                print("trans result is " ,trans_result)
                correct_message = model.ErrorSolutionT5(body_content)
                
                if(correct_message.upper() == body_content.upper()):
                    correcting_message = "NO_CORRECTION"
                else:
                    correcting_message = "correct answer is "+correct_message
                give_word_1, give_word_2 = extraction.word_extraction(given_sentence)
                
                giving_word = "Recommended words: " + give_word_1 + ", " + give_word_2 + " (예시: " + trans_result.text+")"
                result_json_str = json.dumps(
                    {
                        'text':get_second_res[0] +"|" + correcting_message +"|" + giving_word,
                        'id':model_response['id'],
                        'episode_done':model_response['episode_done'],
                        'add_response':body_content
                    }
                )
            else:
                result_json_str = json.dumps(model_response)

            
            print("json_str is ", result_json_str)
            self.wfile.write(bytes(result_json_str, 'utf-8'))

        elif self.path == '/reset':
            self._interactive_running(b"[RESET]")
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(bytes("{}", 'utf-8'))
            message_available.wait()
            message_available.clear()
        else:
            return self._respond({'status': 500})

    def do_GET(self):
        """
        Respond to GET request, especially the initial load.
        """
        paths = {
            '/': {'status': 200},
            '/favicon.ico': {'status': 202},  # Need for chrome
        }
        
        if self.path in paths:
            self._respond(paths[self.path])
        else:
            self._respond({'status': 500})

    def _handle_http(self, status_code, path, text=None):
        self.send_response(status_code)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        content = WEB_HTML.format(STYLE_SHEET, FONT_AWESOME)
        return bytes(content, 'UTF-8')

    def _respond(self, opts):
        response = self._handle_http(opts['status'], self.path)
        self.wfile.write(response)


def on_message(ws, message):
    """
    Prints the incoming message from the server.

    :param ws: a WebSocketApp
    :param message: json with 'text' field to be printed
    """
    incoming_message = json.loads(message)
    global new_message
    new_message = incoming_message['text']
    message_available.set()


def on_error(ws, error):
    """
    Prints an error, if occurs.

    :param ws: WebSocketApp
    :param error: An error
    """
    print(error)


def on_close(ws):
    """
    Cleanup before closing connection.

    :param ws: WebSocketApp
    """
    # Reset color formatting if necessary
    print("Connection closed")


def _run_browser():
    host = opt.get('host', 'localhost')
    serving_port = opt.get('serving_port', 8080)

    httpd = HTTPServer((host, serving_port), BrowserHandler)

    print('Please connect to the link: http://{}:{}/'.format(host, serving_port))

    SHARED['wb'] = httpd

    httpd.serve_forever()


def on_open(ws):
    """
    Starts a new thread that loops, taking user input and sending it to the websocket.

    :param ws: websocket.WebSocketApp that sends messages to a browser_manager
    """
    threading.Thread(target=_run_browser).start()


def setup_args():
    """
    Set up args, specifically for the port number.

    :return: A parser that parses the port from commandline arguments.
    """
    parser = ParlaiParser(False, False)
    parser_grp = parser.add_argument_group('Browser Chat')
    parser_grp.add_argument(
        '--port', default=35496, type=int, help='Port used by the web socket (run.py)'
    )
    parser_grp.add_argument(
        '--host',
        default='localhost',
        type=str,
        help='Host from which allow requests, use 0.0.0.0 to allow all IPs',
    )
    parser_grp.add_argument(
        '--serving_port',
        default=8080,
        type=int,
        help='Port used to configure the server',
    )

    return parser.parse_args()


if __name__ == "__main__":
    opt = setup_args()
    port = opt.get('port', 34596)
    print("Connecting to port: ", port)
    ws = websocket.WebSocketApp(
        "ws://localhost:{}/websocket".format(port),
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
    )
    ws.on_open = on_open
    setup_interactive(ws)
    ws.run_forever()
