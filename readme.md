        _______________ _____ 
       |_  |  ___|  _  \_   _|
         | | |_  | | | | | |
         | |  _| | | | | | |
     /\__/ / |   | |/ / _| |_ 
     \____/\_|   |___/  \___/ 


The build system for people who tolerate batch files and shell scripts for smaller projects.

## Rationale ##

Plenty of build systems aim to scale to large codebases.  They contain knowledge about your environment and aim to automate common tasks.  JFDI scales to the lowend.  It is scripting with helpers and hooks -- designed to let you define your own build logic so you can just get the thing built.  JFDI.

## Features ##

- Tested and nurtured to life on Linux, Macos and Windows with GCC, Clang and MSVC support
- One small Python file with no dependencies other than Python itself.
- Self-propagating: run `build.jfdi` script directly (equivalent to makefiles) to download the jfdi build system.
- Provides an API of conveniently named functions to do common things.
- Generate a self-documented build template to get started with `--init`.
- Portable build scripts that work anywhere Python runs.
- Automatically swaps dir slashes for easy x-platform scripting.

## Sample Script ##

This builds a multi-file C project with clang, putting build products in a `bin/` subdirectory.

    jfdi.py --init  # generate template build file build.jfdi

```Python
# build.jfdi

def start_build():
    arm("clang")
    mkd("bin")
    
def list_input_files():
    return ['hello.c', 'main.c']

def build_this(in_path):
    obj_path = obj(in_path, "bin")
    return exp("$CC $CFLAGS -c $in_path -o $obj_path)

def end_build(in_files):
    objs = obj(in_files, "bin")
    cmd(exp("$LD $LDFLAGS $objs -o bin/hello"))

def clean(in_files):
    rm("bin")
```

    jfdi.py      # builds build.jfdi

See [examples](examples/) for more use cases.

## Changes ##

 - *0.0.2*: September 2018: added `raw()` command to get a filename without extension.
 - *0.0.3*: November 2018:  `cmd()` now returns stdout as newline-trimmed utf-8 string instead of errorlevel

### Versus Makefiles ###

On Windows, GNU Make brings in a Unix runtime (via Cygwin, MSYS2, etc.) which can take up a gigabyte. Furthermore, it handles fork() poorly and whether it uses Unix paths is install-dependent.  The official GNU Make binary is over a decade old and does not work on modern Windows.

GNU Make is, arguably, overkill for smaller projects.

### Versus Batch Files ###

Batch files only run on Windows but JFDI runs on Linux, Mac and Windows.  They are fiddly to write and don't let you easily do things like subsitute one file extension for another.  (`in.c` builds `in.obj`, for instance).

JFDI offers a compact build-specific API.  You will type significantly less to get the same thing built.

### Versus Bash scripts ###

Bash scripts make you use Unix paths on Windows, whereas you often call programs that use Windows paths.  Mixed path scripting is gross.  Bash also depends on cp, rm, chmod, chown and a battery of Unix commands to be available.  Getting a compliant Unix environment up and running is asking a Windows user to install around a gigabyte of exes.

JFDI offers a compact build-specific API.  You will type significantly less to get the same thing built.

### Versus Visual Studio Project files ###

SLN files integrate with Visual Studio which has a debugger, so you should use that if you value that closely knit integration.  However, setting up a project that links against other libraries and has include directories is tedious.  If you have multiple projects with similar configuration needs, JFDI lets you build them all without additional overhead.

SLN files are mostly only forwards compatible.  JFDI lets people with earlier Visual Studio versions than you compile your code.

SLN files will never build on Linux or Macos, but JFDI does.  See the [multi-compiler example](examples/multi_compiler/).

### Versus SCons ###

[SCons](http://scons.org) is a fully featured Python-based software construction tool.  It must be installed in your operating system and forces you to keep the older Python 2 around (whereas JFDI is based on Python 3).  Unlike JFDI, it has deep knowledge about various compilers and imposes conventions through its environment model.

This is a blessing and a curse: if SCons knows about your build environment, you are in luck and can build quickly.  If it does not, adding support for it is involved and poorly documented.  In contrast, JFDI barely knows anything about your toolchain, expecting you to expressly support it using a very simple API.

SCons is not widely installed. Therefore, if you distribute your software, you are asking all of your users to install it and an outdated version of Python on their machines just to build your small program.  JFDI is also not widely installed, but it self propagates and does not need to be installed at the operating system level.  A user simply needs to run the `build.jfdi` script directly to retrieve the latest version.

SCons is a good candidate to upgrade to if your project becomes too large for JFDI.  The author uses it to build production code for a 200 file codebase.

## Usage ##

    jfdi.py --init           # create build.jfdi in cwd
    emacs build.jfdi         # edit self-documenting build script
    jfdi.py                  # run build.jfdi in cwd, building your program

See also: [examples](examples/)

## Documentation ##

API documentation is generated and included in every build script.
Run `jfdi.py --init` to generate one.  Alternatively, read the code to `jfdi.py`'s \_api\_* functions.  It has a very shallow call graph with no dependencies and is easy to read.

# Known Limitations #

This software has been in use for two years on the author's small projects.  It generally works well.  The issues on Github consist of all the known issues.

# Copyright and Credit #

Copyright &copy; 2016-2018 Frogtoss Games, Inc.  File [LICENSE](LICENSE) covers all files in this repo.

JFDI by Michael Labbe. <mike@frogtoss.com>

## Support ##

Directed support for this work is available from the original author under a paid agreement.

[Contact Frogtoss Games](http://www.frogtoss.com/pages/contact.html)
