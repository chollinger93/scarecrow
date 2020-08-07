# CHANGELOG
All changes to the project are documented here.

## [Unreleased]
- Switch to vidgear_async for better performance
- pyPI release 
- Cleaning up model dependencies from path

## [0.4.1] - 2020-08-07

### Added
- Consolidated all units tests to `tests/` 
- Added local `codecov`/`pytest` batches

### Changed
- Updated `setup.py` and `requirements.txt` for a clean install on a fresh machine
- Changed audio test to skip if `pygame` is missing or we cannot check the OS
- Updated `coveragerc` for more accurate coverage

### Removed
- Removed `tests/` from `scarecrow_client`, `scarecrow_server`, `scarecrow_core`

## [0.4] - 2020-06-26
### Added
- New `sleep` logic to save on performance

### Changed
- Separated `client`, `server`, `modules` into separate modules
- Updated `setup.py`
- Fixed unit tests 
- Cleaned up `sbin`

### Removed
- Removed custom `vidgear` dependency, switched to `vidgear==0.18.0`