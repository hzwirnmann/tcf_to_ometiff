# TCF to OME-TIFF Parser
Python package to parse Tomocube TCF (Tomocube Common Format) files to OME-TIFF format.

## Motivation
Holotomography is a microscopy technique to produce label-free 3D images of cells using quantitative phase imaging. The [Tomocube HT-2H](https://www.tomocube.com/product/ht-series/#HT_series_cont) is based on this principle. The images produced with the software provided (TomoStudio) are stored as TCF files (Tomocube Common Format). This project provides a parser that translates this format into a standardized [OME-TIFF](https://docs.openmicroscopy.org/ome-model/5.6.3/ome-tiff/) file where the image is stored as tiff and metadata is compliant with OME-XML specifications.

## Installation
`python -m pip install .`

## Usage
Example data can be found in the `examples` folder.
An overall config file is provided as `examples/overall_config.txt`. See description further below.

### CLI
- Parse a single file that resides in folder _folder_ with the same name as the folder and the extension .TCF:
`python tcf_to_ometiff/cli.py parse <folder> <overall config file path>`

- Parse multiple files that reside in subfolders of folder _top\_folder_, each one having the same name as the subfolder and the extension .TCF:
`python tcf_to_ometiff/cli.py parse-multiple <top_folder> <overall config file path>`

### Programmatically:
- For a single file that resides in folder _20220131.150824.759.Default-001_ with the same name as the folder and the extension .TCF:
```
import tcf_to_ometiff

config_file_path = "./examples/overall_config.txt"
folder = "20220131.150824.759.Default-001"
overall_md = tcf_to_ometiff.create_overall_config(config_file_path)
tcf_to_ometiff.transform_tcf(folder, overall_md)
```

- For multiple files, each coming in one folder that resides in a top folder (here: `examples`):
```
import tcf_to_ometiff

config_file_path = "./examples/overall_config.txt"
top_folder = "examples/"
tcf_to_ometiff.transform_folder(top_folder, config_file_path)
```

## Overall Config File
The overall config file provides values for different meta data such as details about the experimenter and the project. An exemplary config file with all possible values is provided as `examples/overall_config.txt`.

This file is not to be confused with a another config file called `config.dat` that resides in the image folder and that is automatically generated by TomoStudio during image acquisition. Both the overall and the per-image config file are needed for the parsing.

## OME-TIFF Validation
The validation of the correct format of an OME-TIFF XML header is described [here](https://docs.openmicroscopy.org/bio-formats/6.0.1/users/comlinetools/xml-validation.html).

## Requirements
aicsimageio==4.10.0
h5py==3.10.0
numpy==1.25.2
ome-types==0.4.3
typer==0.9.0

## Open Tasks
- Metadata treatment for brightfield (BF) images
- Metadata treatment for 2D and 3D fluorescence (FL) images
- Get correspondence between HT and FL image coordinates right

## License
MIT
