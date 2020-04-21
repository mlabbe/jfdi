# JFDI Changelog #

This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).



All breaking changes are scheduled for major version increases.

## [1.0.4] - April 2020 ##
 - bugfix: `HOST_OS` and `TARGET_OS` are now available in `run()`.

## [1.0.3] - February 2020 ##

### Fixed ###
- `pth()` no longer returns `None` on BSDs
- `use()` now overrides from environment

## [1.0.2] - February 2019 ##

### Fixed ###
- Fixed error on `jfdi -r`

## [1.0.1] - February 2019 ##

### Fixed ###
- Fixed error on `jfdi run`

## [1.0.0] - January 2019 ##

Version was changed to 1.0.0 after successful release candidate period.

## [0.2.1] - January 2019 ##
*Alpha release candidate 1*

## [0.2.0] - January 2019 ##
### Added ###
- `yes()` api call returns boolean for build vars
- extensive built-in documentation revamp

### Changed ###
- `var()` now always returns string.  See `jfdi help buildvars` for details.

## [0.1.0] - January 2019 ##
### Added ###
- Added new `jfdi run` command to just call `run()` and exit.

### Changed ###
- Command line handling now has subcommands similar to git.  `jfdi --init` is now `jfdi init`.

## [0.0.4] - January 2019 ##
### Added ###
- `rm()` now works on list and iter inputs in addition to str
- new, optional `run()` function in build script which executes the build product when `--run` is specified
- pyinstaller now produces standalone jfdi.exe for distribution on Windows

### Changed ###
- `arm()` renamed `use()` to reduce confusion. (All breaking changes scheduled for before 1.0.)
- `JFDI_VERSION` is no longer ignored; must now be 1 to work with working version of jfdi
- all logging messages includes time elapsed with ms precision (where possible)
- `log()` now prints the name of the calling function in the resulting log message to help you debug your build script

### Removed ###
- `arm()` function no longer exists
- `--var` cmdline now implicit; just pass `arg=value` pairs
- `new()` removed; was not effective anyway

### Fixed ###
- `obj()` iter input returns list, as expected



## [0.0.3] - November 2018 ##
### Changed ###
- `cmd()` now returns stdout as newline-trimmed utf-8 string instead of errorlevel



## [0.0.2] - September 2018 ##
### Added ###
- `raw()` command to get a filename without extension
