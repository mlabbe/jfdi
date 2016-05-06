        _______________ _____ 
       |_  |  ___|  _  \_   _|
         | | |_  | | | | | |
         | |  _| | | | | | |
     /\__/ / |   | |/ / _| |_ 
     \____/\_|   |___/  \___/ 


The build system for people who tolerate batch files and shell scripts for smaller projects.

## Rationale ##

Plenty of build systems aim to scale to large codebases.  They contain knowledge about your environment and aim to automate common tasks.  JFDI scales to the lowend.  It is bare Python scripting with helpers and hooks -- designed to let you define your own build logic so you can just get the thing built.

## Features ##

- One small Python file with no dependencies other than Python itself.
- Self-propagating: run `build.jfdi` script directly (equivalent to makefiles) to download the jfdi build system.
- Provides an API of conveniently named functions to do common things.
- Generate a self-documented build template to get started with `--init`.
- Portable build scripts that work anywhere Python runs.

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
    return exp("$CC $CFLAGS -c " + in_path + " -o " + obj_path)

def end_build(in_files):
    objs = obj(in_files, "bin")
    cmd(exp("$LD $LDFLAGS " + objs + "-o bin/hello"))

def clean(in_files):
    arm("clang")
    for file in in_files:
        rm(obj(file, "bin"))
    rm("bin")
```

    jfdi.py      # builds build.jfdi

See [examples](examples/) for more use cases.

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

## Usage ##

    jfdi.py --init           # create build.jfdi in cwd
    emacs build.jfdi         # edit self-documenting build script
    jfdi.py                  # run build.jfdi in cwd, building your program

See also: [examples](examples/)

## Documentation ##

API documentation is generated and included in every build script.
Run `jfdi.py --init` to generate one.  Alternatively, read the code to `jfdi.py`'s \_api\_* functions.  It has a very shallow call graph with no dependencies and is easy to read.

# Known Limitations #

This software is in beta and hasn't been thoroughly tested yet.  This message will be removed as the author uses it more heavily.

# Copyright and Credit #

Copyright &copy; 2016 Frogtoss Games, Inc.  File [LICENSE](LICENSE) covers all files in this repo.

JFDI by Michael Labbe. <mike@frogtoss.com>

## Support ##

Directed support for this work is available from the original author under a paid agreement.

[Contact Frogtoss Games](http://www.frogtoss.com/pages/contact.html)
