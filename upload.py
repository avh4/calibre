#!/usr/bin/python
import sys, glob, os, subprocess, time, shutil
sys.path.append('src')
from subprocess import check_call as _check_call
from functools import partial
from pyvix.vix import *

PREFIX = "/var/www/vhosts/kovidgoyal.net/subdomains/libprs500"
DOWNLOADS = PREFIX+"/httpdocs/downloads"
DOCS = PREFIX+"/httpdocs/apidocs"
HTML2LRF = "src/libprs500/ebooks/lrf/html/demo"
TXT2LRF  = "src/libprs500/ebooks/lrf/txt/demo"
check_call = partial(_check_call, shell=True)
h = Host(hostType=VIX_SERVICEPROVIDER_VMWARE_WORKSTATION)

def build_windows():
    files = glob.glob('dist/*.exe')
    for file in files:
        os.unlink(file)
    
    
    
    vm = h.openVM('/mnt/vista/Windows Vista/Windows Vista.vmx')
    vm.powerOn() 
    if not vm.waitForToolsInGuest():
        print >>sys.stderr, 'Windows is not booting up'
        sys.exit(1)
    
    
    
    vm.loginInGuest('kovid', 'et tu brutus')
    vm.loginInGuest(VIX_CONSOLE_USER_NAME, '')
    vm.runProgramInGuest('C:\\Users\kovid\Desktop\libprs500.bat', '')
    if not glob.glob('dist/*.exe'):
        raise Exception('Windows build has failed')
    vm.runProgramInGuest('C:\Windows\system32\shutdown.exe', '/s')
    return os.path.basename(glob.glob('dist/*.exe')[-1])

def build_osx():
    files = glob.glob('dist/*.dmg')
    for file in files:
            os.unlink(file)
    if os.path.exists('dist/dmgdone'):
        os.unlink('dist/dmgdone')
    
    vm = h.openVM('/mnt/osx/Mac OSX/Mac OSX.vmx')
    vm.powerOn()
    c = 25 * 60
    print 'Waiting (minutes):',
    while c > 0 and not os.path.exists('dist/dmgdone'):
        time.sleep(10)
        c -= 10
        if c%60==0:
            print c/60, ',',
            sys.stdout.flush()
    print
        
    if not os.path.exists('dist/dmgdone'):
        raise Exception('OSX build has failed')
    vm.powerOff()
    return os.path.basename(glob.glob('dist/*.dmg')[-1])
    


def upload_demo():
    check_call('''html2lrf --title='Demonstration of html2lrf' --author='Kovid Goyal' '''
               '''--header --output=/tmp/html2lrf.lrf %s/demo.html '''
               '''--serif-family "/usr/share/fonts/corefonts, Times New Roman" '''
               '''--mono-family  "/usr/share/fonts/corefonts, Andale Mono" '''
               ''''''%(HTML2LRF,))
    check_call('cd src/libprs500/ebooks/lrf/html/demo/ && zip /tmp/html-demo.zip * /tmp/html2lrf.lrf')
    check_call('''scp /tmp/html-demo.zip castalia:%s/'''%(DOWNLOADS,))
    check_call('''txt2lrf -t 'Demonstration of txt2lrf' -a 'Kovid Goyal' '''
               '''--header -o /tmp/txt2lrf.lrf %s/demo.txt'''%(TXT2LRF,) )
    check_call('cd src/libprs500/ebooks/lrf/txt/demo/ && zip /tmp/txt-demo.zip * /tmp/txt2lrf.lrf')
    check_call('''scp /tmp/txt-demo.zip castalia:%s/'''%(DOWNLOADS,))

def upload_installers(exe, dmg):
    check_call('''ssh castalia rm -f %s/libprs500\*.exe'''%(DOWNLOADS,))
    check_call('''scp dist/%s castalia:%s/'''%(exe, DOWNLOADS))
    check_call('''ssh castalia rm -f %s/libprs500\*.dmg'''%(DOWNLOADS,))
    check_call('''scp dist/%s castalia:%s/'''%(dmg, DOWNLOADS))
    check_call('''ssh castalia chmod a+r %s/\*'''%(DOWNLOADS,))
    check_call('''ssh castalia /root/bin/update-installer-links %s %s'''%(exe, dmg))

def upload_docs():
    check_call('''epydoc --config epydoc.conf''')
    check_call('''scp -r docs/html castalia:%s/'''%(DOCS,))
    check_call('''epydoc -v --config epydoc-pdf.conf''')
    check_call('''scp docs/pdf/api.pdf castalia:%s/'''%(DOCS,))

    

def main():
    upload = len(sys.argv) < 2
    shutil.rmtree('build')
    os.mkdir('build')
    shutil.rmtree('docs')
    os.mkdir('docs')
    check_call("sudo python setup.py develop", shell=True)
    check_call('make', shell=True)
    check_call('svn commit -m "Updated translations" src/libprs500/translations')
    upload_demo()
    print 'Building OSX installer...'
    dmg = build_osx()
    print 'Building Windows installer...'
    exe = build_windows()
    if upload:
        print 'Uploading installers...'
        upload_installers(exe, dmg)
        print 'Uploading to PyPI'
        check_call('''python setup.py register bdist_egg --exclude-source-files upload''')
        upload_docs()
        check_call('''rm -rf dist/* build/*''')
    
if __name__ == '__main__':
    main()
