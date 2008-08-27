#!/usr/bin/env  python

__license__   = 'GPL v3'
__copyright__ = '2008, Kovid Goyal <kovid at kovidgoyal.net>'
'''
Embedded console for debugging.
'''

import sys, os, re
from calibre.utils.config import OptionParser
from calibre.constants import iswindows, isosx
from calibre.libunzip import update

def option_parser():
    parser = OptionParser(usage='''\
%prog [options]

Run an embedded python interpreter.
''')
    parser.add_option('--update-module', help='Update the specified module in the frozen library. '+
    'Module specifications are of the form full.name.of.module,path_to_module.py', default=None
    )
    parser.add_option('-c', '--command', help='Run python code.', default=None)
    return parser

def update_zipfile(zipfile, mod, path):
    if 'win32' in sys.platform:
        print 'WARNING: On Windows Vista using this option may cause windows to put library.zip into the Virtual Store (typically located in c:\Users\username\AppData\Local\VirtualStore). If it does this you must delete it from there after you\'re done debugging).' 
    pat = re.compile(mod.replace('.', '/')+r'\.py[co]*')
    name = mod.replace('.', '/') + os.path.splitext(path)[-1]
    update(zipfile, [pat], [path], [name])


def update_module(mod, path):
    if not hasattr(sys, 'frozen'):
        raise RuntimeError('Modules can only be updated in frozen installs.')
    zp = None
    if iswindows:
        zp = os.path.join(os.path.dirname(sys.executable), 'library.zip')
    elif isosx:
        zp = os.path.join(os.path.dirname(getattr(sys, 'frameworks_dir')),
                            'Resources', 'lib', 'python2.5', 'site-packages.zip')
    if zp is not None:
        update_zipfile(zp, mod, path)
    else:
        raise ValueError('Updating modules is not supported on this platform.')

def main(args=sys.argv):
    opts, args = option_parser().parse_args(args)
    if opts.update_module:
        mod, path = opts.update_module.partition(',')[0], opts.update_module.partition(',')[-1]
        update_module(mod, os.path.expanduser(path))
    elif opts.command:
        sys.argv = args[:1]
        exec opts.command
    else:
        from IPython.Shell import IPShellEmbed
        ipshell = IPShellEmbed()
        ipshell()



    return 0

if __name__ == '__main__':
    sys.exit(main())
