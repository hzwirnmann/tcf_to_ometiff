# Change Log

## Version 0.4.0 (December 14, 2023)

- Added support for fluorescence images
- Added annotations from image metadata
- Remodelled channel information
- Remodelled light source information
- Timestamp information is now extracted from the tcf file on a per-image base instead of the separate timestamp file
- Additional per-image metadata is read from file "JobParameter.tcp" that is created by TomoStudio for each tcf file. I.e., complete metadata is now "overall metadata created by user" + "per image metadata created automatically by TomoStudio" where the latter consists of the two files "config.dat" and "JobParameter.tcp" that have 75% redundant information.

## Version 0.3.0 (December 12, 2023)

- Added support for brightfield image
- Added changelog

## Version 0.2.0 (December 8, 2023)

- Changes to keep up with updated ome-types v0.4.0 dependency
- Updated license to MIT
- Updates to README
- Added pyproject.toml

## Version 0.1.0 (February 7, 2023)

- Initial commit
