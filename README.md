# TCF to OME-TIFF Parser
Python tool to parse Tomocube TCF (Tomocube Common Format) files to OME-TIFF format.

## Motivation
Holotomography is a microscopy technique to produce label-free 3D images of cells using quantitative phase imaging. The [Tomocube HT-2H](https://www.tomocube.com/product/ht-series/#HT_series_cont) is based on this principle. The images produced with the software provided (TomoStudio) are stored as TCF files (Tomocube Common Format). This parser translates this format into a standardized [OME-TIFF](https://docs.openmicroscopy.org/ome-model/5.6.3/ome-tiff/) file where the image is stored as tiff and metadata is compliant with OME-XML specifications.

## Usage
_python tcf_to_ometiff.py \<image top folder path\> \<config file path\>_

## Config file
The config file provides values for different meta data such as details about the experimenter and the project. An exemplary config file with all possible values is provided as config.txt.

## Requirements
h5py

ome_types

aicsimageio
  
## ToDos
- Metadata treatment for brightfield (BF) images
- Metadata treatment for 2D and 3D fluorescence (FL) images
- Get correspondence between HT and FL image coordinates right
- Docstrings
