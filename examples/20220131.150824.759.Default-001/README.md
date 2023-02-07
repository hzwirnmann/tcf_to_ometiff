# Example TCF - OME-TIFF Conversion

## Download
Files can be downloaded under this link (large file size): https://syncandshare.lrz.de/getlink/fiPqd3jPq4egLyJsiC8NiP/20220131.150824.759.Default-001   

## File Contents
20220131.150824.759.Default-001.TCF: original image file with 3D HT image and 2D HT MIP (maximum intensity projection)   
config.dat: per-image metadata created by TomoStudio - not to be confused with the user-generated overall config file
20220131.150824.759.Default-001.ome.tiff: OME-TIFF created using tcf_to_ometiff   
20220131.150824.759.Default-001.ome.xml: OME-XML header extracted from OME-TIFF

## How to Reproduce
From tcf\_to\_ometiff repo base folder that contains the overall config file `overall_config.txt`:
`python tcf_to_ometiff/cli.py parse examples/20220131.150824.759.Default-001 overall_config.txt`
