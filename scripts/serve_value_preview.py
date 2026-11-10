#!/usr/bin/env python3
"""Serve an in-memory Value Theory draft preview; never writes public HTML."""
import argparse
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote,urlsplit
import build_value_full_editions as b

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--port',type=int,default=8788)
 a=p.parse_args()
 outputs={str(path.relative_to(b.ROOT)):text.encode() for path,text in b.render(partial=True).items()}
 class Handler(SimpleHTTPRequestHandler):
  def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(b.ROOT),**kwargs)
  def log_message(self,*args):pass
  def do_GET(self):
   path=unquote(urlsplit(self.path).path).lstrip('/')
   if path.endswith('/'):path+='index.html'
   if path in outputs:
    body=outputs[path]
    self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8')
    self.send_header('Content-Length',str(len(body)));self.send_header('Cache-Control','no-store');self.end_headers();self.wfile.write(body)
   else:super().do_GET()
 print('LOCAL DRAFT PREVIEW, not published or accepted:',sum(path.name!='index.html' and path.parent.name in b.LANGS for path in b.render(partial=True)),'complete article drafts;',len(outputs),'in-memory pages',flush=True)
 try:ThreadingHTTPServer(('127.0.0.1',a.port),Handler).serve_forever()
 except KeyboardInterrupt:pass

if __name__=='__main__':main()
