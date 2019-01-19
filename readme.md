        _______________ _____ 
       |_  |  ___|  _  \_   _|
         | | |_  | | | | | |
         | |  _| | | | | | |
     /\__/ / |   | |/ / _| |_ 
     \____/\_|   |___/  \___/ 


The build system for people who tolerate batch files and shell scripts for smaller projects.

## Rationale ##

Plenty of build systems aim to scale to large codebases.  They contain knowledge about your environment and aim to automate common tasks.  JFDI scales to the lowend.  It is scripting with helpers and hooks -- designed to let you script your own build logic so you can just get the thing built.  **JFDI.**

## Un-features ##

- Designed to scale to the small-end only
- Not destined to be fast for managing large builds
- Not the author's big idea of a perfect build system
- No definition format to learn, just code in Python with a batchy api

## Features ##

- Just code your build in portable Python using functions designed to make building convenient
- Self-propagating: end-user runs the build script directly to download the jfdi build system
- Tested and nurtured to life on Linux, Macos and Windows with GCC, Clang and MSVC support
- First class support for non-compiler building (LaTeX, shaders, etc.)
- Build system will always be one small Python file with no dependencies other than Python
- Provides a small API to simplify build tasks; much less wordy than stock Python libraries
- Generate a self-documented build template to get started with `--init`
- Portable build scripts that work anywhere Python runs
- Automatically swaps dir slashes for easy x-platform scripting
- Used by the author for a ton of small projects for 3 years and counting

## Sample Script ##

This builds a multi-file C project with clang, putting build products in a `bin/` subdirectory.

    # get the latest stable jfdi
    wget https://raw.githubusercontent.com/mlabbe/jfdi/master/jfdi.py

    # generate template build file build.jfdi
    jfdi.py --init

```Python
# build.jfdi

def start_build():
    # set CC, LD, etc. to common clang values
    use("clang")
    # make subdir if it doesn't exist
    mkd("bin")


# list all files to compile.
def list_input_files():
    # wildcards are welcome
    return ['hello.c', 'main.c', '*.c']


# called once per file that will be compiled
def build_this(in_path):

    # given path to source file, get a path to the output .o
    # note this would automatically be .obj if msvc was used
    obj_path = obj(in_path, "bin")

    # return the command to build this file
    # exp expands $-based variables
    return exp("$CC $CFLAGS -c $in_path -o $obj_path)


# called once at the end of a build
def end_build(in_files):
    # given a list of all input source files, get a list of
    # all obj files
    objs = obj(in_files, "bin")

    # cmd executes a command line program which must succeed to continue
    cmd(exp("$LD $LDFLAGS $objs -o bin/hello"))


# called when the user uses jfdi -c
def clean(in_files):
    # rm deletes a directory or file
    rm("bin")
```

    jfdi.py      # builds build.jfdi

See [examples](examples/) for more use cases.

## Changelog ##

Changes are described in [CHANGELOG.md](CHANGELOG.md).

### Versus Makefiles ###

On Windows, GNU Make brings in a Unix runtime (via Cygwin, MSYS2, etc.) which can take up a gigabyte. Furthermore, it handles fork() poorly and whether it uses Unix paths is install-dependent.  The official GNU Make binary is over a decade old and does not work on modern Windows.

GNU Make is, arguably, overkill for smaller projects.

### Versus Batch Files ###

Batch files only run on Windows but JFDI runs on Linux, Mac and Windows.  They are fiddly to write and don't let you easily do things like subsitute one file extension for another.  (`in.c` builds `in.obj`, for instance).

JFDI offers a compact build-specific API.  You will type significantly less to get the same thing built.

### Versus Bash scripts ###

Bash scripts make you use Unix paths on Windows, whereas you often call programs that use Windows paths.  Mixed path scripting is gross.  Bash also depends on cp, rm, chmod, chown and a battery of Unix commands to be available.  Getting a compliant Unix environment up and running is asking a Windows user to install around a gigabyte of exes.

If you use bash files you have to explicitly check every command for errorlevel and exit on failure.  JFDI implicitly assumes your build fails when the compiler returns errors.

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

### Extended Usage ###

    jfdi.py DEBUG=1          # pass build variable DEBUG to build script, var('DEBUG') returns 1

See also: [examples](examples/)

## Documentation ##

API documentation is generated and included in every build script.
Run `jfdi.py --init` to generate one.  Alternatively, read the code to `jfdi.py`'s \_api\_* functions.  It has a very shallow call graph with no dependencies and is easy to read.

# Known Limitations #

This software has been in use for three years on the author's small projects.  The issues on Github consist of all the known issues.

# Copyright and Credit #

Copyright &copy; 2016-2019 Frogtoss Games, Inc.  File [LICENSE](LICENSE) covers all files in this repo.

JFDI by Michael Labbe. <mike@frogtoss.com>

## Support ##

Directed support for this work is available from the original author under a paid agreement.

[Contact Frogtoss Games](http://www.frogtoss.com/pages/contact.html)
