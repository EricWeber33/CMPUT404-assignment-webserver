#  coding: utf-8 
import socketserver

from os.path import exists, isdir


# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v - 

# http response constants


OK = 200
MOVED = 301
BAD_REQUEST = 400
NOT_FOUND = 404
METHOD_NOT_ALLOWED = 405

class MyWebServer(socketserver.BaseRequestHandler):

    http_responses = {
        200: 'OK',
        301: 'Moved Permanently',
        400: 'Bad Request',
        404: 'Not Found',
        405: 'Method Not allowed'
    }

    response = ""

    def handle(self):
        self.data = self.request.recv(1024).strip()
        print ("Got a request of: %s\n" % self.data)
        method, resource, location = self.parse_request(self.data)
        if method == None or resource == None:
            self.add_and_complete_response_header(BAD_REQUEST)
        elif method == 'GET':
            self.do_get(resource, location=location)  
        elif method in ['POST', 'DELETE', 'PUT', 'PATCH', 'HEAD', 'TRACE', 'CONNECT', 'OPTIONS']:
            self.add_and_complete_response_header(METHOD_NOT_ALLOWED)
        else:
            self.add_and_complete_response_header(BAD_REQUEST)
        self.send_full_response()
            


    def do_get(self, resource, location=None):
        """
        handles the case of a get request
        param: resource (string) is a path to a requested resource
        """
        if not self._is_valid_request(resource):
            return
        root_dir = './www'
        if resource[-1] == '/':
            resource += 'index.html'
        full_path = root_dir + resource
        if exists(full_path):
            if isdir(full_path):
                self.send_moved_response(resource, location)
                return
            with open(root_dir+resource, 'r') as f:
                content = f.read()
            self.add_respose_header(OK)
            if resource.endswith('.html'):
                self.response += 'Content-Type: text/html\r\n'
                #self.request.sendall(bytearray('Content-Type: text/html\r\n', 'utf-8'))
            elif resource.endswith('.css'):
                self.response += 'Content-Type: text/css\r\n'
                #self.request.sendall(bytearray('Content-Type: text/css\r\n', 'utf-8'))
            self.add_newline()
            self.response += content
            #self.request.sendall(bytearray(content, 'utf-8'))
            self.add_newline()
        else:
            self.add_and_complete_response_header(NOT_FOUND)


    def _is_valid_request(self, resource) -> bool:
        if resource[0] != '/':
            self.add_and_complete_response_header(BAD_REQUEST)
            return False
        if not self._is_secure(resource):
            self.add_and_complete_response_header(NOT_FOUND)
            return False
        return True


    def _is_secure(self, path) -> bool:
        """
        Checks that path will not access files 'above' the intended
        root directory is being accessed.

        param path: the path to the requested resource, should not include the './www' prefix
        """
        path_parts = path.split('/')
        prior_directories = 0
        jump_backs = 0
        for part in path_parts:
            if part == '..':
                jump_backs += 1
            else:
                prior_directories += 1
            if jump_backs > prior_directories:
                return False
        return True


    def parse_request(self, request_data):
        try:
            data_parts = request_data.split()
            method = data_parts[0].decode('utf-8').strip()
            resource = data_parts[1].decode('utf-8').strip()
            location = data_parts[4].decode('utf-8').strip()
            return (method, resource, location)
        except IndexError:
            return (None, None, None)

    def send_moved_response(self, resource, location):
        self.add_respose_header(MOVED)
        link = f'http://{location+resource}/'
        location_message = f'Location: {link}\r\n'
        self.response += location_message
        #self.request.sendall(bytearray(location_message, 'utf-8'))
        self.add_newline()


    def add_and_complete_response_header(self, code):
        self.add_respose_header(code)
        self.add_newline()


    def add_respose_header(self, code):
        response_header = f'HTTP/1.1 {code} {self.http_responses[code]}\r\n'
        self.response += response_header
        #self.request.sendall(bytearray(response, 'utf-8'))


    def add_newline(self):
        self.response += '\r\n'
        #self.request.sendall(bytearray('\r\n', 'utf-8'))

    def send_full_response(self):
        self.request.sendall(bytearray(self.response, 'utf-8'))
        self.request = ''

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
