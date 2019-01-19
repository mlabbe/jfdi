# JFDI Changelog #

This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

All breaking changes are scheduled for major version increases.

## [0.0.4] - January 2019 ##
### Added ###
- `rm()` now works on list and iter inputs in addition to str

### Changed ###
- `arm()` renamed `use()` to reduce confusion. (All breaking changes scheduled for before 1.0.)

### Removed ###
- `arm()` function no longer exists
- `--var` cmdline now implicit; just pass `arg=value` pairs 

### Fixed ###
- `obj()` iter input returns list, as expected

## [0.0.3] - November 2018 ##
### Changed ###
- `cmd()` now returns stdout as newline-trimmed utf-8 string instead of errorlevel

## [0.0.2] - September 2018 ##
### Added ###
- `raw()` command to get a filename without extension