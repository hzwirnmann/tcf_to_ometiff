# TCF to OME-TIFF Parser
Python package to parse Tomocube TCF (Tomocube Common Format) files to OME-TIFF format.

## Motivation
Holotomography is a microscopy technique to produce label-free 3D images of cells using quantitative phase imaging. The [Tomocube HT-2H](https://www.tomocube.com/product/ht-series/#HT_series_cont) is based on this principle. The images produced with the software provided (TomoStudio) are stored as TCF files (Tomocube Common Format). This parser translates this format into a standardized [OME-TIFF](https://docs.openmicroscopy.org/ome-model/5.6.3/ome-tiff/) file where the image is stored as tiff and metadata is compliant with OME-XML specifications.

## Installation
_python setup.py install_

## Usage
Via CLI:
Parse a single file that resides in folder _folder_ with the same name as the folder and the extension .TCF:
_python tcf_to_ometiff/cli.py parse \<folder\> \<config file path\>_

Parse multiple files that reside in subfolders of folder _top\_folder_, each one having the same name as the subfolder and the extension .TCF:
_python tcf_to_ometiff/cli.py parse-multiple \<top_folder\> \<config file path\>_

## Config File
The config file provides values for different meta data such as details about the experimenter and the project. An exemplary config file with all possible values is provided as config.txt.

## OME-XML Validation
The validation of the correct format of an OME-TIFF XML header is described [here](https://docs.openmicroscopy.org/bio-formats/6.0.1/users/comlinetools/xml-validation.html).

## Requirements
aicsimageio==4.9.4
h5py==3.8.0
numpy==1.23.1
ome-types==0.3.3
typer==0.7.0

## ToDos
- Metadata treatment for brightfield (BF) images
- Metadata treatment for 2D and 3D fluorescence (FL) images
- Get correspondence between HT and FL image coordinates right
- Docstrings
