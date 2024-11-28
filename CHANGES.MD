# Change Log

## Version 0.5.2 (November 28, 2024)

- minor changes to reflect ome-types v0.5.3 (e.g. include ExperimenterGroup)

## Version 0.5.1 (November 28, 2024)

- change from aicsimageio to bioio for writing
- updates to tiling
- updated links and versions in Readme

## Version 0.5.0 (November 26, 2024)

- bugfix overall config
- updated tiling info
- added Planes info for pixels

## Version 0.4.7 (June 27, 2024)

- included time zone information so the acquisition datetime shown in OMERO is the same as in the .ome.tiff (see related discussion: https://forum.image.sc/t/omero-webclient-import-date-modify-timezone/54384 )

## Version 0.4.6 (June 3, 2024)

- Added support to include tiling information over several pictures as additional annotation

## Version 0.4.5 (May 7, 2024)

- Added Stage to Pixels elements including information about x/y/z/exposure time

## Version 0.4.4 (February 19, 2024)

- Added StageLabel property for 3D fluorescence image that includes the Z shift in µm between plane 0 of the HT image and plane 0 of the FL image.

## Version 0.4.3 (February 8, 2024)

- Minor fix: Generated OME.XML is now valid again, wasn't before because the same channel ID got used for several images produced with the same light source, e.g., 3D HT, 2D HT and HT MIP got assigned the same channel ID previously

## Version 0.4.2 (February 8, 2024)

- Minor changes to reflect ome-types v0.4.5 (StructuredAnnotations instead of StructuredAnnotationsList)

## Version 0.4.1 (December 15, 2023)

- Added `--output-xml` option to CLI to enable outputting the .ome.xml file alongside the .ome.tiff file (default: False)
- Added some backwards compatibility for old TomoStudio versions that output incomplete config metadata

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
