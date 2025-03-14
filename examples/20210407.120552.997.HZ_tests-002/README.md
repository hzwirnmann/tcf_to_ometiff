# Example TCF - OME-TIFF Conversion

## Download
Files can be downloaded under this link (large file size): https://syncandshare.lrz.de/getlink/fi9XKfRhH8CKWh6EYx7wA5/20210407.120552.997.HZ_tests-002

## Folder Contents
`20210407.120552.997.HZ_tests-002.TCF`: original image file with 3D HT image and 2D HT MIP (maximum intensity projection)  
`20210407.120552.997.HZ_tests-002.ome.tiff`: OME-TIFF created using tcf\_to\_ometiff  
`20210407.120552.997.HZ_tests-002.ome.xml`: OME-XML file  
`config.dat`: per-image metadata file created by TomoStudio - not to be confused with the user-generated overall config file  
`JobParameter.tcp`: another per-image metadata file created by TomoStudio

## How to Reproduce
From tcf\_to\_ometiff repo base folder that contains the overall config file `examples/overall_config.txt`:
`python tcf_to_ometiff/cli.py parse examples/20210407.120552.997.HZ_tests-002 examples/overall_config.txt`
