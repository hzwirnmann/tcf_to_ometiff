# Example TCF - OME-TIFF Conversion

## Download
Files can be downloaded under this link (large file size): https://syncandshare.lrz.de/getlink/fiPqd3jPq4egLyJsiC8NiP/20220131.150824.759.Default-001

## Folder Contents
`20220131.150824.759.Default-001.TCF`: original image file with 3D HT image and 2D HT MIP (maximum intensity projection)  
`20220131.150824.759.Default-001.ome.tiff`: OME-TIFF created using tcf\_to\_ometiff  
`20220131.150824.759.Default-001.ome.xml`: OME-XML header extracted from OME-TIFF  
`config.dat`: per-image metadata created by TomoStudio - not to be confused with the user-generated overall config file
`JobParameter.tcp`: another per-image metadata created by TomoStudio

## How to Reproduce
From tcf\_to\_ometiff repo base folder that contains the overall config file `examples/overall_config.txt`:
`python tcf_to_ometiff/cli.py parse examples/20220131.150824.759.Default-001 examples/overall_config.txt`
