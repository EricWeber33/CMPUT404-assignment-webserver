#  coding: utf-8 
from http.client import BAD_REQUEST
import socketserver

from os.path import exists
from urllib import request

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
        301: 'Moved',
        400: 'Bad Request',
        404: 'Not Found',
        405: 'Method Not allowed'
    }

    def handle(self):
        self.data = self.request.recv(1024).strip()
        print ("Got a request of: %s\n" % self.data)
        method, resource = self.parse_request(self.data)
        print(method == 'GET')
        if method == 'GET':
            self.do_get(resource)
        elif method in ['POST', 'DELETE', 'PUT', 'PATCH']:
            self.send_response_header(METHOD_NOT_ALLOWED)
            return
        else:
            self.send_response_header(BAD_REQUEST)
            return
        self.request.sendall(bytearray("OK",'utf-8'))


    def do_get(self, resource):
        """
        handles the case of a get request
        param: resource (string) is a path to a requested resource
        """
        if not self._is_valid_request(resource):
            return
        root_dir = './www'
        if exists(root_dir + resource):
            if resource[-1] != '/':
                self.send_moved_response(resource)
                return
        else:
            self.send_response_header(NOT_FOUND)
            return
    
    def _is_valid_request(self, resource) -> bool:
        if resource[0] != '/':
            self.send_response_header(BAD_REQUEST)
            return False
        if not self._is_secure(resource):
            self.send_response_header(NOT_FOUND)
            return False
        return True


    def send_moved_response(self, resource):
        self.send_response_header(MOVED)
        return

    def _is_secure(self, path) -> bool:
        """
        Checks that path will not access files 'above' the intended
        root directory

        if at any point in the path there are more instances of '..' than 
        prior 'named' directories then a directory above 'www' is being accessed.

        param path: the path to the requested resource, should not include the './www' prefix
        """
        path_parts = path.split('/')
        prior_directories = 0
        jump_backs = 0
        for part in path_parts:
            if part == '..':
                jump_backs += 1
            else:
                prior_directories +=1
            if jump_backs > prior_directories:
                return False
        return True
            
    def parse_request(self, request_data):
        data_parts = request_data.split()
        method = data_parts[0].decode('utf-8').strip()
        resource = data_parts[1].decode('utf-8').strip()
        print(type(method), method)
        print(type(resource), resource)
        return (method, resource)

    def send_response_header(self, code):
        response = f'HTTP/1.1 {code} {self.http_responses[code]}\r\n'
        print(response)
        self.request.send(bytearray(response, 'utf-8'))



if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
