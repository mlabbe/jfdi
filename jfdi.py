#!/usr/bin/env python3

# JFDI is
# Copyright (C) 2016-2019 Frogtoss Games, Inc.
#
# Author Michael Labbe
# See LICENSE in this repo for license terms
#
# latest version, examples and documentation:
# https://github.com/mlabbe/jfdi.git

# todo:
# - handle OSError could not rmdir because a dos prompt is in it
# - JFDI_VERSION in generated script does not match VERSION here

import sys
if sys.version_info[0] < 3:
    sys.stderr.write('JFDI requires Python 3\n')
    sys.exit(1)

import os
import sys
import glob
import time
import shutil
import os.path
import argparse
import platform
import subprocess

VERSION=(0,0,4)

_cfg = {}

def _is_jfdi_compatible_with_build_script_version():
    """is this version of jfdi.py compatible with the build format version?
    The value is stored in JFDI_VERSION in the generated template.

    None return value means it's compatible"""
    script_version = int(globals()['JFDI_VERSION'])
    
    if script_version == 1:
        return None
    
    elif script_version > 1:
        return " is too old for build script JFDI_VERSION %d" % (script_version)
    
    elif script_version < 1:
        return " is too new for build script JFDI_VERSION %s" % (script_version)

        

def _parse_args():
    global cfg

    desc = "JFDI Simple Build System version %d.%d" % (VERSION[0], VERSION[1])
    p = argparse.ArgumentParser(description=desc,
                                usage="%(prog)s [options] [var=value ...]")
    p.add_argument('-v', '--verbose', help="increase verbosity",
                   action='store_true')
    p.add_argument('-f', '--file', help='read FILE as build.jfdi')
    p.add_argument('-c', '--clean', help="clean the build and exit",
                   action='store_true')
    p.add_argument('--target-os', help='specify TARGET_OS for cross compiling')
    p.add_argument('--init', help="create new build.jfdi file in CWD",
                   action='store_true')
    p.add_argument('-F', '--force', help='force rebuild -- new() always true',
                   action='store_true')
                   
    args, unknown = p.parse_known_args()
    _cfg['args'] = args

    # unknown arg parse sets variables 
    # some var facts:
    #  - case insensitive
    #  - accessed with var(key, type), where type can be bool, int, str
    #  - if no equals sign, then default to int(1) for value
    vars = {}
    for v in unknown:
        var = v.split('=', 1)

        # all vars are uppercase
        ukey = var[0].upper()

        if len(var) == 2:
            vars[ukey] = var[1]
        else:
            vars[ukey] = 1

    if _cfg['args'].verbose:
        for v in vars:
            print("build var %s = %s" % (v, vars[v]))

    _cfg['vars'] = vars

    return args

def _which(file):
    for path in os.environ["PATH"].split(os.pathsep):
        if os.path.exists(os.path.join(path, file)):
            return os.path.join(path, file)
    return None

def _pp_version():
    """pretty print version as a string"""
    return '.'.join(str(i) for i in VERSION)

def _message(verbosity, in_msg):
    global cfg

    if in_msg.__class__ == list:
        msg = ' '.join(in_msg)
    else:
        msg = in_msg
        
    if verbosity >= 1 and not _cfg['args'].verbose:
        return
    print(msg)

def _warning(msg):
    sys.stderr.write("warning: " + msg)

def _fatal_error(msg, error_code=1):
    sys.stderr.write(msg)
    sys.stderr.write("exiting with error code %d\n" % error_code)
    sys.exit(error_code)

def _get_script():
    """compiled contents of script or error out"""
    DEFAULT_SCRIPT = 'build.jfdi'

    script_path = None
    if os.path.exists(DEFAULT_SCRIPT):
        script_path = DEFAULT_SCRIPT

    global _cfg
    if _cfg['args'].file:
        script_path = _cfg['args'].file

    if script_path == None or not os.path.exists(script_path):
        fatal_msg =  "Build file not found\n"
        fatal_msg += "If starting from scratch, use %s --init\n" \
                     % sys.argv[0]
        fatal_msg += "%s --help for detailed help.\n\n" \
                     % sys.argv[0]
        _fatal_error(fatal_msg)

    _cfg['script_path'] = script_path
    _cfg['script_mtime'] = os.path.getmtime(script_path)

    with open(script_path) as f:
        script = f.read()

    try:
        pycode = compile(script, script_path, mode='exec')
    except SyntaxError as ex:
        msg =  "SyntaxError in (%s, line %d):\n\t%s\n" \
               % (ex.filename, ex.lineno, ex.text)
        _fatal_error(msg)
    return pycode

def _swap_slashes(dir):
    if platform.system() == 'Darwin' or platform.system() == 'Linux':
        return dir.replace('\\', '/')

    if platform.system() == 'Windows':
        return dir.replace('/', '\\')

def _add_api(g):
    g['ext'] = _api_ext
    g['log'] = _api_log
    g['mkd'] = _api_mkd
    g['cmd'] = _api_cmd
    g['die'] = _api_die
    g['cp']  = _api_cp
    g['rm']  = _api_rm
    g['env'] = _api_env
    g['use'] = _api_use
    g['arg'] = _api_arg
    g['obj'] = _api_obj
    g['var'] = _api_var
    g['new'] = _api_new
    g['exe'] = _api_exe
    g['exp'] = _api_exp
    g['pth'] = _api_pth
    g['raw'] = _api_raw
    return g

def _run_script(pycode):
    g = _add_api(globals())

    push_name = globals()['__name__']
    globals()['__name__'] = '__jfdi__'
    exec(pycode, g)
    globals()['__name__'] = push_name

    #
    # validate expected functions
    #
    
    # todo: fill this out
    missing_msg = ""
    if 'list_input_files' not in g:
        missing_msg += "list_input_files() must exist\n"

    if 'JFDI_VERSION' not in g:
        missing_msg += "JFDI_VERSION must exist in build script\n"

    if len(missing_msg) != 0:
        sys.stderr.write("errors were found during execution:\n")
        _fatal_error(missing_msg)

    #
    # validate version compatibility
    #
    error_result = _is_jfdi_compatible_with_build_script_version()
    if error_result != None:
        _fatal_error("JFDI %s%s\n" % (_pp_version(), error_result))
        
    
    context = [globals()]
    return context

def _handle_input_files(input_files):
    if input_files.__class__ == str:
        input_files = [input_files]

    out_paths = []
        
    for entry in input_files:
        if '*' in entry:
            wildcard = glob.glob(entry)
            for path in wildcard:
                out_paths.append(path)
        else:
            out_paths.append(entry)

    return out_paths

# deprecated
def _handle_str_input_files_old(input_files):
    out_files = []
    if '*' in input_files:
        wildcard = glob.glob(input_files)
        for path in wildcard:
            if os.path.isfile(path):
                out_files.append(path)
    else:
        out_files.append(input_files)

    return out_files
    


def _build(context):
    global _cfg
    globals()['HOST_OS'] = platform.system()
    globals()['TARGET_OS'] = platform.system()
    if _cfg['args'].target_os:
        globals()['TARGET_OS'] = _cfg['args'].target_os
        
    input_files = context[0]['list_input_files']()
    input_files = _handle_input_files(input_files)
    if _cfg['args'].clean:
        _message(1, "cleaning")
        context[0]['clean'](input_files)
        sys.exit(0)

    context[0]['start_build']()
        
    cmd_list = []
    for path in input_files:
        cmd = context[0]['build_this'](path)
        if cmd != None:
            cmd_list.append(cmd)

    _message(1, "building %d/%d file(s)" %
             (len(cmd_list), len(input_files)))
    
    for cmd in cmd_list:
        _run_cmd(cmd)

    context[0]['end_build'](input_files)

def _run_cmd(cmd):
    _message(0, cmd)
    exit_code = subprocess.call(cmd, shell=True)
    if exit_code != 0:
        _fatal_error("error '%d' running command \"%s\"\n" %
                     (exit_code, cmd))

def _report_success(start_time):
    end_time = time.time()
    delta_time = end_time - start_time
    _message(0, "success in %.1f seconds." % delta_time)

def _str_to_list(val):
    """If val is str, return list with single entry, else return as-is."""
    l = []
    if val.__class__ == str:
        l.append(val)
        return l
    else:
        return val

def _list_single_to_str(val):
    """If val is len(list) 1, return first entry, else return as-is."""
    if val.__class__ == list and len(val) == 1:
        return val[0]
    else:
        return val
        
def generate_tmpl(path):
    if os.path.exists(path):
        _fatal_error("%s already exists.\n" % path)

    f = open(path, "wt")
    f.write("""\
#    _______________ _____ 
#   |_  |  ___|  _  \_   _|
#     | | |_  | | | | | |  
#     | |  _| | | | | | |  
# /\__/ / |   | |/ / _| |_ 
# \____/\_|   |___/  \___/ 
#
# NOTE:
# if you do not have jfdi.py, run this script with python to get it.
# or clone https://github.com/mlabbe/jfdi
\"""
jfdi build script

available functions:
  cp(src, dst)  - copy a file or directory
  rm(str|iter)  - remove file or directory
  arg(str)      - convert a /flag into a -flag depending on compiler
  use('?')      - add make-like variables (LD, CC, etc.). gcc, clang, msvc
  cmd(list|str) - run a command on a shell, fatal if error, stdout returns as str
  die(str)      - fail build with a message, errorlevel 3
  env(str)      - return environment variable or None
  exe(str)      - return filename with exe extension based on TARGET_OS
  exp(str)      - expand a $string, searching CLI --vars and then global scope
  ext(str)      - return file extension         (file.c = .c)
  raw(str)      - return file without extension (file.c = file)
  log(str)      - print to stdout
  mkd(str)      - make all subdirs
  new(src,dst)  - true if file src is newer than file dst
  obj(str)      - return filename with obj file ext (file.c = file.obj)
  pth(str)      - swap path slashes -- \ on windows, / otherwise
  var(str,type) - get command line var passed in during build instantiation

variables:
  HOST_OS       - compiling machine OS    (str)
  TARGET_OS     - target machine OS       (str)

after use(), variables, where applicable:
  CC            - c compiler
  CXX           - c++ compiler
  LD            - linker
  OBJ           - obj extension (ex: 'obj')
  CCTYPE        - compiler 
  CFLAGS        - list of c flags
  CXXFLAGS      - list of c++ flags
  LDFLAGS       - list of linker flags
  
\"""

JFDI_VERSION = 1

# called at the start of the build
def start_build():
    pass

# return a list of files
def list_input_files():
    return []


# return command to build single file in_path or None to skip
def build_this(in_path):
    return None

# called after every input file has been built
def end_build(in_files):
    pass

# called when the user requests --clean
def clean(in_files):
    pass


    
#
# main -- installs build system if build script is run directly
#
# generated code: do not edit this
#
if __name__ == '__main__':
    import sys
    import os.path
    import urllib.request
    
    print("You have run the build script directly.")
    print("Expected Usage: python jfdi.py -f %s" %
          sys.argv[0])

    DST_FILENAME = 'jfdi.py'
    if os.path.exists(DST_FILENAME):
        sys.exit(0)
    print("Do you want to download the JFDI build script?")
    yesno = input('Y/n -->')
    if yesno == 'n':
        sys.exit(0)

    print("downloading jfdi.py")
    url = "https://raw.githubusercontent.com/mlabbe/jfdi/master/jfdi.py"
    urllib.request.urlretrieve(url, DST_FILENAME)
    
    print("%s downloaded." % DST_FILENAME)
    print("Usage: python %s -f %s" %
          (DST_FILENAME, sys.argv[0]))
    print("To permanently install jfdi, manually copy jfdi.py into your search path.")
    sys.exit(0)

""")
    f.close()
        
#
# api 
#
def _api_ext(x):
    return os.path.splitext(x)[1]

def _api_raw(x):
    return os.path.splitext(x)[0]

def _api_log(msg):
    print("log:\t%s" % msg)

def _api_mkd(dirs):
    dirs = _swap_slashes(dirs)
    _message(1, "making dirs %s" % dirs)
    os.makedirs(dirs, exist_ok=True)

def _api_cmd(cmd):
    if cmd.__class__ == list:
        _message(0, ' '.join(cmd))
    else:
        _message(0, cmd)

    proc = subprocess.Popen(cmd, shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    out, err = proc.communicate()
    ret = proc.returncode

    if len(err) != 0:
        _warning(err.decode('utf-8'))

    if ret != 0:
        _fatal_error("\nerror code %d running \"%s\"\n" % (ret, cmd),
                     error_code=ret)

    return out.rstrip().decode('utf-8')

def _api_cp(src, dst):
    if os.path.isdir(src):
        _message(0, "recursively copy %s to %s" % (src, dst))
        shutil.copytree(src, dst)
    else:
        _message(0, "cp %s to %s" % (src, dst))
        shutil.copy2(src, dst)

def _api_die(msg):
    sys.stderr.write("die: " + msg + "\n")
    sys.exit(3)

def _api_rm(files):

    file_list = _str_to_list(files)

    for f in file_list:
        if not os.path.exists(f):
            _message(1, "rm nonexistent %s" % f)
            continue

        f = _swap_slashes(f)
    
        if os.path.isdir(f):
            _message(0, "rmdir %s" % f)
            shutil.rmtree(f, ignore_errors=False)
        else:
            _message(0, "rm %s" % f)
            os.remove(f)

def _api_env(e):
    if e not in os.environ:
        return None
    return os.environ[e]

def _api_use(id):
    v = {}
    if id[:4] == 'msvc':
        v['CC'] = 'cl.exe'
        v['CXX'] = v['CC']
        v['OBJ'] = 'obj'
        v['LD'] = 'link.exe'
        v['CCTYPE'] = 'msvc'
        v['CFLAGS'] = []
        v['CXXFLAGS'] = []
        v['LDFLAGS'] = []
        
    elif id == 'clang':
        v['CC'] = 'clang'
        v['CXX'] = 'clang++'
        v['OBJ'] = 'o'
        v['LD'] = 'clang'   # /usr/bin/ld is too low-level
        v['CCTYPE'] = 'gcc' # clang is gcc-like
        v['CFLAGS'] = []
        v['CXXFLAGS'] = []
        v['LDFLAGS'] = []

    elif id == 'gcc':
        v['CC'] = 'gcc'
        v['CXX'] = 'g++'
        v['OBJ'] = 'o'
        v['LD'] = 'gcc'     # /usr/bin/ld is too low-level
        v['CCTYPE'] = 'gcc'
        v['CFLAGS'] = []
        v['CXXFLAGS'] = []
        v['LDFLAGS'] = []
        

    else:
        msg =  "use() unknown ID '%s'\n" % (id)
        msg += "acceptable Ids:\n"
        msg += "\tmsvc, clang, gcc\n"
        _fatal_error(msg)

    if _which(v['CC']) == None:
        _warning("use(): compiler '%s' not found in search path.\n" % v['CC'])

    if _which(v['LD']) == None:
        _warning("use(): linker '%s' not found in search path.\n" % v['LD'])

    g = globals()
    for var in v:
        g[var] = v[var]

def _api_arg(flag):
    if 'CCTYPE' not in globals():
        _fatal_error("must call use() before arg()")

    i = 0
    if flag[0] == '-' or flag[0] == '/':
        i = 1

    if globals()['CCTYPE'] == 'msvc':
        symbol = '/'
    else:
        symbol = '-'
        
    return symbol + flag[i:]


def _api_obj(path, in_prefix_path=''):
    prefix_path = _swap_slashes(in_prefix_path)
    if 'CCTYPE' not in globals():
        _fatal_error('you must call use() before calling obj()\n')

    in_paths = _str_to_list(path)
    out_paths = []
    
    ext = ''
    if globals()['CCTYPE'] == 'msvc':
        ext = '.obj'
    elif globals()['CCTYPE'] == 'gcc':
        ext = '.o'

    for p in in_paths:
        split = os.path.splitext(p)

        filename = split[0] + ext
        path = os.path.join(prefix_path, filename)
        
        out_paths.append(path)

    return _list_single_to_str(out_paths)
    

def _api_obj_old(path, in_prefix_path=''):
    prefix_path = _swap_slashes(in_prefix_path)
    if 'CCTYPE' not in globals():
        _fatal_error('you must call use() before calling obj()\n')

    # FIXME: don't join this; it makes passing it to rm() impossible
    #
    # rm(obj(in_files)) should be a common use pattern.
    if path.__class__ == list:
        obj_str = ''
        for p in path:
            split = os.path.splitext(p)
            if globals()['CCTYPE'] == 'msvc':
                obj = '.obj'
            elif globals()['CCTYPE'] == 'gcc':
                obj = '.o'
            file_str = '%s%s ' % (split[0], obj)
            obj_str += os.path.join(prefix_path, file_str)
        return obj_str

    # str case
    split = os.path.splitext(path)
    
    obj = ''
    if globals()['CCTYPE'] == 'msvc':
        obj = '.obj'
    elif globals()['CCTYPE'] == 'gcc':
        obj = '.o'

    file_str = split[0] + obj
    return os.path.join(prefix_path, file_str)
    
    

def _api_var(key,type=str):
    global _cfg

    ukey = key.upper()
    if ukey in _cfg['vars']:
        val = _cfg['vars'][ukey]

        # workaround: string 0 would be true
        if type == bool and val == '0':
            val = 0
        
        try:
            tval = type(val)
        except ValueError:
            tval = val
        return tval
    return ''

def _api_new(src, dst):
    if _cfg['args'].force:
        return True
    
    if not os.path.exists(dst):
        return True

    src_mtime = os.path.getmtime(src)
    dst_mtime = os.path.getmtime(dst)    
    
    return src_mtime > dst_mtime

def _api_exe(path, append_if_debug=None):
    split = os.path.splitext(path)

    exe = ''
    if globals()['TARGET_OS'] == 'Windows':
        exe = '.exe'

    base_str = str(split[0])
    if append_if_debug != None and _api_var('DEBUG', bool):
        base_str += append_if_debug

    return base_str + exe

def _api_exp(in_str):
    _message(1, "expanding \"%s\"" % in_str)
    out = ''

    reading_var = False
    for i in range(0, len(in_str)):
        c = in_str[i]
        if c == ' ':
            reading_var = False
            
        if reading_var:
            continue
            
        if c == '$':
            reading_var = True
            var = in_str[i:].split(' ')[0]
            if len(var) == 1:
                out += c
                reading_var = False
                continue

            var = var[1:]
            if len(var) > 1:
                val = None
                
                # scan calling function first
                frame = sys._getframe(1)
                if var in frame.f_locals:
                    val = frame.f_locals[var]
                    
                # scan vars second (command line override)                
                elif var in _cfg['vars']:
                    
                    val = _cfg['vars'][var]
                # check environment variables, third
                elif var in os.environ:
                    val = os.environ[var]
                    
                # fall back to global vars
                elif var in globals():
                    val = globals()[var]
                else:
                    
                    _fatal_error("exp(): var %s not found.\n" % var)
                    
            if val.__class__ == list:
                val = ' '.join(str(x) for x in val)

            out += val
        else:
            out += c
                
    return out

def _api_pth(path):
    return _swap_slashes(path)
        
#
# main
#

if __name__ == '__main__':
    start_time = time.time()
    args = _parse_args()

    if args.init:
        generate_tmpl('build.jfdi')
        sys.exit(0)
    
    pycode = _get_script()
    context = _run_script(pycode)
    _build(context)

    _report_success(start_time)
    sys.exit(0)

