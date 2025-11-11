#!/usr/bin/env python3
"""
健康检查接口
"""

import json
from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        response = {
            "status": "ok",
            "service": "wechat-server",
            "version": "1.0.0",
            "platform": "vercel"
        }

        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))