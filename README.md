# TCF to OME-TIFF Parser
Python package to parse Tomocube TCF (Tomocube Common Format) files to OME-TIFF format. [Link to this repo](https://github.com/hzwirnmann/tcf_to_ometiff)

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

- If you want to output the `.ome.xml` for the image as a separate file, append the option `--output-xml` to the 
command from above.

### Programmatically:
- For a single file that resides in folder _20220131.150824.759.Default-001_ with the same name as the folder and the extension .TCF:
```
import tcf_to_ometiff

config_file_path = "./examples/overall_config.txt"
folder = "20220131.150824.759.Default-001"
overall_md = tcf_to_ometiff.create_overall_config(config_file_path)
tcf_to_ometiff.transform_tcf(folder, overall_md, output_xml=False)
```

- For multiple files, each coming in one folder that resides in a top folder (here: `examples`):
```
import tcf_to_ometiff

config_file_path = "./examples/overall_config.txt"
top_folder = "examples/"
tcf_to_ometiff.transform_folder(top_folder, config_file_path, output_xml=False)
```

- If you want to output the `.ome.xml` for the image(s) as a separate file, change the `output_xml` parameter to `True`. 

## Overall Config File
The overall config file provides values for different meta data such as details about the experimenter and the project
that do not follow from the per-image metadata that are automatically created. An exemplary config file with all 
necessary values is provided as `examples/overall_config.txt`.

This file is not to be confused with the other config files called `config.dat` and `JobParameter.tcp` that reside in
the image folder and that are automatically generated by TomoStudio during image acquisition. Both the overall and the
per-image config files are needed for the parsing.

## OME-TIFF Validation
The validation of the correct format of an OME-TIFF XML header is described [here](https://docs.openmicroscopy.org/bio-formats/6.0.1/users/comlinetools/xml-validation.html).

## Requirements
aicsimageio==4.14.0  
h5py==3.10.0  
numpy==1.26.4  
ome-types==0.4.5  
typer==0.9.0

## Open Tasks
- Add support for tiling

## Acknowledgments
Thanks to the OME team for their work on imaging standardization and reproducibility. Special thanks to Josh Moore,
Talley Lambert, Dan, Sébastien Besson and Christoph Gohlke, who provided support to help me understand the OME 
XML schema in [this thread](https://forum.image.sc/t/setting-up-ome-xml-for-a-new-microscope-from-scratch/62116) on the image.sc forum.

## Citing this Project
If this work is helpful for your research, you can cite the [corresponding paper](https://www.sciencedirect.com/science/article/pii/S2405896323012429):
```
@article{ZWIRNMANN20236477,
title = {Towards End-to-End Automated Microscopy Control using Holotomography: Workflow Design and Data Management},
journal = {IFAC-PapersOnLine},
volume = {56},
number = {2},
pages = {6477-6483},
year = {2023},
note = {22nd IFAC World Congress},
issn = {2405-8963},
doi = {https://doi.org/10.1016/j.ifacol.2023.10.862},
url = {https://www.sciencedirect.com/science/article/pii/S2405896323012429},
author = {Henning Zwirnmann and Dennis Knobbe and Sami Haddadin},
keywords = {Biomedical and medical image processing and systems, Bio-signals analysis and interpretation, Bioinformatics, Human centred automation},
abstract = {Microscopy has been a key tool involved in many discoveries in the life sciences over the past centuries. In the last 30 years in particular, enormous progress has been made in developing this measurement technique further to make researchers working with it more effective. To combine gains in reproducibility and efficiency resulting from these advancements in different research areas, we present for the first time a unified and comprehensive concept for an end-to-end automated microscopy workflow. To this end, we employ both robotic and computational methods as well as holotomography microscopy. Considering the physical preparation and cleanup of a measurement, the image acquisition, and the management and analysis of the resulting data, we give a fine-grained workflow description. We present the robotic system to perform the manual process steps and a Python package to standardize the resulting proprietary image (meta)data. For the other tasks, we identify suitable open-source tools to execute them and apply them to our setup. The choice of holotomography as a suitable microscopy technique to realize this workflow is elucidated. We envision that the adoption of an automated workflow paves the way toward a future life science laboratory where microscopy-based research is carried out more efficiently and reproducibly than in the past.}
}
```

## License
MIT
