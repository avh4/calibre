#!/usr/bin/env python
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai
from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

__license__   = 'GPL v3'
__copyright__ = '2011, Kovid Goyal <kovid@kovidgoyal.net>'
__docformat__ = 'restructuredtext en'

'''
Utilities to help with developing coffeescript based apps
'''
import time, SimpleHTTPServer, SocketServer, os, bz2, sys
from io import BytesIO

from PyQt4.QtWebKit import QWebPage

try:
    from calibre.gui2 import must_use_qt
    must_use_qt
except ImportError:
    import init_calibre
    init_calibre
    from calibre.gui2 import must_use_qt
from calibre import force_unicode
from calibre.gui2 import FunctionDispatcher

must_use_qt()

class Compiler(QWebPage): # {{{

    def __init__(self):
        QWebPage.__init__(self)
        self.frame = self.mainFrame()
        self.filename = self._src = ''
        compiler = bz2.decompress(P('coffee-script.js.bz2', data=True))
        self.frame.evaluateJavaScript(compiler)
        self.frame.addToJavaScriptWindowObject("cs_compiler", self)
        self.dispatcher = FunctionDispatcher(self.__evalcs, parent=self)
        self.errors = []

    def shouldInterruptJavaScript(self):
        return True

    def javaScriptConsoleMessage(self, msg, lineno, sourceid):
        sourceid = sourceid or self.filename or '<script>'
        self.errors.append('%s:%s'%(sourceid, msg))

    def __evalcs(self, raw, filename=None):
        # This method is NOT thread safe
        self.filename = filename
        self.setProperty('source', raw)
        self.errors = []
        res = self.frame.evaluateJavaScript('''
            raw = document.getElementById("raw");
            raw = cs_compiler.source;
            CoffeeScript.compile(raw);
        ''')
        ans = ''
        if res.type() == res.String:
            ans = unicode(res.toString())
        return ans, self.errors

    def __call__(self, raw, filename=None):
        raw = force_unicode(raw)
        return self.dispatcher(raw, filename=filename)
# }}}

# FAVICON {{{
FAVICON = \
b'\x00\x00\x01\x00\x01\x00\x00\x00\x00\x00\x01\x00 \x00\x9c\x04\x00\x00\x16\x00\x00\x00\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x10\x00\x00\x00\x10\x08\x03\x00\x00\x00(-\x0fS\x00\x00\x02IPLTE\x00\x00\x00888\x0c\x0c\x0c\x12\x12\x12\x1b\x1b\x1b\x16\x16\x16I\x00\x00J\x00\x00\x17\x17\x17\x14\x14\x14\x10\x10\x10$$$""" ##\x19\x1c\x1c\x02\x07\x07\x81\x06\x0eT\t\x0e\x08\x11\x10\x0e\x0e\x0e\x1e\x1e\x1e\t\t\t\x06\x06\x06\xae\x1c\x1d\xa5\x1d\x1e\x8b\x18\x19\x87\x15\x15,\x16\x16!\x14\x15KJJ\x1f\x1f\x1f\x1d\x1d\x1d333\x05\x05\x05\x04\x04\x04"\x02\x03\x0f\x00\x02\x13\x13\x13\x0f\x0f\x0f\x0c\x0c\x0c\x0c\x0c\x0c\x11\x11\x11\x11\x11\x11\x0f\x10\x10"\n\nR\x00\x00L\x00\x00\x1c\r\r\x12\x13\x13\x13\x16\x16$\x13\x136\x04\x07!\x1a\x14)\x1c\x118\x04\x04\x1f\x15\x15\x10\x14\x14\x1e\x1f#74\x1e\x7fn\x1c5.\x172+\x11|j\x12<:\'\x1e\x1f#\r\x14$_S\x11\x8a|.[N\x05UJ\x0e\x03\x0b\x1f$\n\x0cO\r\x0bL\t\x080\x13\x15\x07\x07\x07\x13\x1f\x1fd\x12\x17\xd2\x05\nl\x15\x1b\n\x1b\x1a$##\x08\x08\x08\x12\x14\x14*\x17\x19X\x1a\x1fw %\'\x16\x18\x12\x13\x13\x05\x05\x05\n\n\n\x00\x0e\r\x91\x17\x1c\\"#l#%\x9a\x17\x1d\x00\t\t\x08\x08\x08\xa4$%\xc5"#\xbb  \xa1#$\x8a&\'\xbe&&\xbc))\x83\x1d\x1d$\x18\x18w\x1e\x1fp\x1f\x1f\x1d\x13\x14\x1d\x1e\x1e8\x15\x18!\x07\x08)\t\n=\x14\x17\x19\x1b\x1b\x16\x16\x16\x15\x16\x16$\x0c\x0e9\x02\x04[\x00\x01T\x00\x01=\x02\x04+\x1c\x1d%%%\'\'\'\x01\x01\x01\x10\x10\x10\x16\x16\x16\x00\x05\x02H\x00\x04S\x01\x02Y\x05\x05F\x02\x03C\x00\x01I\x00\x03\n\x16\x15%%%###\x00\x00\x00\x08\x08\x08\n\n\n!\x01\x023\x08\t\x1e\x04\x04\x0e\x00\x00\x16\x16\x16\x1a\x1a\x1aXWR\x18\x17\x12R+#JG:-)\x1c9\x10\x0b\xd2\x03\x07\xdd4(`M7[E1\xd8\x1d\x14\xb2\x14\x14\xf1`ak?@`,-\xe1\x1b\x1c\x9c\x15\x15\xa3\r\r\xe1!"\xcb,,\xd623\xdc\x16\x16\x99\r\rq\n\n<\x0f\x0f\xa4\x0e\x0e\x92\x13\x131\x11\x11\x92\x08\x08x\x07\x07<\x08\x08\x9c\x03\x03~\x06\x06\x1e\x0b\x0b\x83\n\n\x89\x04\x04\xb3\x00\x00\xb5\x02\x02\xb7\x03\x03\x9b\x01\x01\x81\x08\x08w\x00\x00\x86\x02\x02\x85\x02\x02r\x01\x01[\x02\x02N\x02\x02WT>\xb4\x00\x00\x00\x94tRNS\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x12\x06\t\x112@\n\x10A*\x1al:22>h\x12%r\x90\xe8\xe5\x86v\x1b\x1a\xad\xf9\xf8\xa5\x120\xd5\xc5\x1e\x03.\xc5\xfc\xa8"\x02\x06E[\xd8\xcc[B\x04\x04\x11(\xe4\xde$\x16\x030\xeb\xe6\'#\xe2\xda\x1b:\xd3\xd7-Q|\xf7\xf3\x90U\x11p*\x9f\xfe\xfd\x96?m\t\x03=.\x01\x15\x83\xc7\xc6|\x12\x0665\x01\x01\n\x03\x11\x10\x02\x02\nEu\xb9r\x00\x00\x00\tpHYs\x00\x00\x00H\x00\x00\x00H\x00F\xc9k>\x00\x00\x00\xf7IDAT\x18\xd3c````T\xd7`b``\xd6\xd4ba\x80\x00Vm\x1d]6v=}\x03\x0e\xa8\x00\xa7\xa1\x91\xb1\x89\xa9\x99\xb9\x05\x17T\x80\xdb\xd2\xca\xda\xc6\xd6\xce\xde\x81\x07*\xc0\xeb\xe8\xe4<e\xaa\x8b\xab\x1b\x1f\x84\xcf/\xe0\xee1m\xfa\x8c\x99\x9e^\x82B \xbe\xb0\xb7\x8f\xef\xac\xd9s\xe6\xce\xf3\xf3\x0f\x08\x14a`\x10\r\n\x0e\t\x9d\xbf`\xe1\xa2\xc5K\xc2\xc2#"E\x19D\xa3\xa2cb\x97.[\xbeb\xe5\xaa\xb8\xf8\x84D1\xa0\x1e\xf1\xa4\xe4\xd5k\xd6\xae[\xbf!%U\x02l\xa8dZ\xfa\xc6M\x9b\xb7l\xdd\x96\x91)\x05\x16\x90\xce\xca\xde\xbec\xe7\xae\xdd{rre\xc0\x02\xb2y\xf9\x05{\xf7\xed?PXT,\x07\xe2\xcb\x97\x94\x96\x95W\x1c<TYU]S\xab\xc0\xc0\xa0XW\xdf\xd0\xd8\xd4\xdc\xd2\xda\xd6\xde\xd1\xd9\xd5\xad\xc4\xa0\xd8\xd3\xdb\xa3\xa4\xdc\xd7?a\xa2\x8a\xea\xa4\xc9j\x8a\x00W\xf7J\xfe\xc9Y\x97\xae\x00\x00\x00%tEXtdate:create\x002011-11-06T14:56:51+05:00t\xf3K\xf2\x00\x00\x00%tEXtdate:modify\x002011-11-06T14:56:51+05:00\x05\xae\xf3N\x00\x00\x00\x00IEND\xaeB`\x82'
# }}}

class Handler(SimpleHTTPServer.SimpleHTTPRequestHandler): # {{{

    special_resources = {}
    compiled_cs = {}

    def send_bytes(self, raw, mimetype, mtime):
        self.send_response(200)
        self.send_header("Content-type", str(mimetype))
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Last-Modified", self.date_time_string(int(mtime)))
        self.end_headers()
        return BytesIO(raw)

    def send_head(self):
        path = self.path
        if path.endswith('.coffee'):
            path = path[1:] if path.startswith('/') else path
            path = self.special_resources.get(path, path)
            raw, mtime = self.compile_coffeescript(path)
            return self.send_bytes(raw, 'text/javascript', mtime)
        if path == '/favicon.ico':
            return self.send_bytes(FAVICON, 'image/x-icon', 1000.0)

        return SimpleHTTPServer.SimpleHTTPRequestHandler.send_head(self)

    def translate_path(self, path):
        path = self.special_resources.get(path, path)
        if path.endswith('/jquery.js'):
            return P('content_server/jquery.js')

        return SimpleHTTPServer.SimpleHTTPRequestHandler.translate_path(self,
                path)

    def guess_type(self, path):
        ans = SimpleHTTPServer.SimpleHTTPRequestHandler.guess_type(self, path)
        return ans

    def newer(self, src, dest):
        try:
            sstat = os.stat(src)
        except:
            time.sleep(0.01)
            sstat = os.stat(src)
        return sstat.st_mtime > dest

    def compile_coffeescript(self, src):
        raw, mtime = self.compiled_cs.get(src, (None, 0))
        if self.newer(src, mtime):
            mtime = time.time()
            with open(src, 'rb') as f:
                raw = f.read()
            cs, errors = compile_coffeescript(raw)
            for line in errors:
                print(line, file=sys.stderr)
            if not cs:
                print('Compilation of %s failed'%src)
                cs = '''
                // Compilation of coffeescript failed
                alert("Compilation of %s failed");
                '''%src
            raw = cs.encode('utf-8')
            self.compiled_cs[src] = (raw, mtime)
        return raw, mtime

class HTTPD(SocketServer.TCPServer):
    allow_reuse_address = True

# }}}

compile_coffeescript = Compiler()

def serve(resources={}, port=8000):
    Handler.special_resources = resources
    httpd = HTTPD(('0.0.0.0', port), Handler)
    print('serving at localhost:%d'%port)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        raise SystemExit(0)

def main():
    import argparse
    parser = argparse.ArgumentParser(description=
            'Compile coffeescript to javascript and print to stdout. Errors '
            'and warnings are printed to stderr.')
    parser.add_argument('src', type=argparse.FileType('rb'),
            metavar='path/to/script.coffee', help='The coffee script to compile. Use '
            ' - for stdin')
    args = parser.parse_args()
    ans, errors = compile_coffeescript(args.src.read(), filename=args.src.name)
    for line in errors:
        print(line, file=sys.stderr)
    if ans:
        print (ans.encode(sys.stdout.encoding or 'utf-8'))

if __name__ == '__main__':
    main()
