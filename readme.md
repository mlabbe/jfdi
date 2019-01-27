        _______________ _____ 
       |_  |  ___|  _  \_   _|
         | | |_  | | | | | |
         | |  _| | | | | | |
     /\__/ / |   | |/ / _| |_ 
     \____/\_|   |___/  \___/ 


The build system for people who tolerate batch files and shell scripts for smaller projects.  Comfortable like an old shoe.

## Rationale ##

JFDI scales *down* to tiny codebases. It is portable build scripting with helper functions -- designed to let you assemble your own build logic so you can just get the thing built.  **J. F. D. I.**

JFDI is trivial to distribute to end users of your code.

See "Why JFDI?" below for a comparison with alternatives.

## Un-features ##

- Designed to scale to the small-end only
- Not destined to be fast for managing large builds
- Not the author's big idea of a perfect build system
- No definition format to learn, just code in Python with a helpful, optional api

## Features ##

- Just code your build in portable Python using functions designed to make building convenient
- Self-propagating: end-user runs the build script directly to download the jfdi build system
- Standalone win32 exe: Your Windows users don't even need a Python install.
- Portable build scripts that work anywhere Python runs
- Tested and nurtured to life on Linux, Macos and Windows with GCC, Clang and MSVC support
- First class support for non-compiler building (LaTeX, shaders, etc.)
- Build system will always be one small Python file with no third party dependencies.
- Provides a small API to simplify build tasks; much less typing than stock Python libraries
- Generate a self-documented build template to get started with `init`
- Automatically swaps dir slashes for easy x-platform scripting
- Used by the author for a handful of small projects for three years and counting

## Installation ##

*Windows*: Download a standalone exe from the Github [releases tab](https://github.com/mlabbe/jfdi/releases) and unzip it to your `PATH`.  Alternatively, run `python jfdi.py <args>` with your preinstalled Python 3 interpreter.

*Linux and Mac*:

    wget https://raw.githubusercontent.com/mlabbe/jfdi/master/jfdi.py && \
    chmod +x jfdi.py && \
    sudo mv jfdi.py /usr/local/bin/jfdi

JFDI has zero third party Python dependencies and is a single file standalone program.  The master branch of the [official github repo](https://github.com/mlabbe/jfdi) is always stable.

## Sample Auto-Generated Build Script ##

This builds a multi-file C project with clang, putting build products in a `bin/` subdirectory.

    # generate template build file build.jfdi
    jfdi init

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


# called when the user uses jfdi clean
def clean(in_files):
    # rm deletes a directory or file
    rm("bin")
```

    jfdi        # builds build.jfdi

See [examples](examples/) for more use cases.


## Documentation ##

1. `jfdi init` creates a build file which contains documentation in comments.
2. See [examples](examples/) for specific usage examples.
3. Questions or suggestions? Post an issue on the official Github repo.
4. Read the code to `jfdi.py`'s \_api\_* functions.  It is not deeply nested and easy to read. Try it out!

## Usage ##

    jfdi init             # create build.jfdi in cwd
    emacs build.jfdi      # edit self-documenting build script
    jfdi                  # run build.jfdi in cwd, building your program

### Extended Usage ###

    jfdi DEBUG=1          # pass build variable DEBUG to build script, yes('DEBUG') returns True
    jfdi clean DEBUG=1    # call build.jfdi clean() which cleans up the build
    jfdi run              # build normally, then call run(), which performs a canonical run
                          # of the build product

See also: [examples](examples/)

## Changelog ##

Changes are described in [CHANGELOG.md](CHANGELOG.md).

# Why JFDI? #

### Versus Makefiles ###

JFDI is meant for tiny projects.  It does not have a dependency graph and it does not support incremental building.  If you desire this, your project is not tiny and you should use something else.

On Windows, GNU Make brings in a Unix runtime (via Cygwin, MSYS2, etc.) which can take up a gigabyte. Furthermore, it handles fork() poorly and whether it uses Unix paths is install-dependent.  The official GNU Make binary is over a decade old and does not work on modern Windows.

GNU Make is, arguably, overkill for smaller projects.

JFDI is a standalone script or executable capable of performing shell-like commands portably.  Thanks to Python's extensive standard library, this includes things like recursively creating directories and zipping up files.

### Versus Batch Files ###

Batch files only run on Windows but JFDI runs on Linux, Mac and Windows.  They are fiddly to write and don't let you easily do things like subsitute one file extension for another.  (`in.c` builds `in.obj`, for instance).

JFDI offers a compact build-specific API.  You will type significantly less to get the same thing built.

### Versus Bash scripts ###

Bash scripts make you use Unix paths on Windows, whereas you often call programs that use Windows paths.  Mixed path scripting is gross.  Bash also depends on cp, rm, chmod, chown and a battery of Unix commands to be available.  Getting a compliant Unix environment up and running is asking a Windows user to install around a gigabyte of exes.

If you use bash files you have to explicitly check every command for errorlevel and exit on failure.  JFDI implicitly assumes your build fails when the compiler returns errors.

JFDI offers a compact build-specific API.  You will type significantly less to get the same thing built.

### Versus Visual Studio Project files ###

SLN files integrate with Visual Studio which has a debugger, so you should use that if you value that closely knit integration.

SLN files are mostly only forwards compatible.  JFDI lets people with earlier Visual Studio versions than you compile your code.

SLN files will never build on Linux or Macos, but JFDI does.  See the [multi-compiler example](examples/multi_compiler/).

SLN files are unspeakably inappropriate for tasks outside of traditional compiling like building a LaTeX book.  JFDI is a better fit for non-code compilation building.

### Versus SCons ###

[SCons](http://scons.org) is a fully featured Python-based software construction tool.  It must be installed on your operating system.  In contrast, JFDI is a standalone exe or script that can be easily downloaded or distributed.

Scons, unlike JFDI, has deep knowledge about various compilers and imposes conventions through its environment model.  Modifying it to do something it previously did not is often not worth the effort.

This is a blessing and a curse: if SCons knows about your build environment, you are in luck and can build quickly.  If it does not, adding support for it is involved and poorly documented.  In contrast, JFDI barely possesses any conventions that enforce a toolchain, expecting you to expressly support it using a very simple API.

SCons is not widely installed. Therefore, if you distribute your software, you are asking all of your users to install it and an outdated version of Python on their machines just to build your small program.  JFDI is also not widely installed, but it self propagates and does not need to be installed at the operating system level.  A user simply needs to run the `build.jfdi` script directly to retrieve the latest version.

# Known Limitations #

By design, JFDI has no dependency graph.  Every file in your project is re-processed when the build script is re-run.

This software has been in use for three years on the author's small projects.  The issues on Github consist of all the known issues.

# Copyright and Credit #

Copyright &copy; 2016-2019 Frogtoss Games, Inc.  File [LICENSE](LICENSE) covers all files in this repo.

JFDI by Michael Labbe. <contact@frogtoss.com>

## Support ##

Directed support for this work is available from the original author under a paid agreement.

[Contact Frogtoss Games](http://www.frogtoss.com/pages/contact.html)
