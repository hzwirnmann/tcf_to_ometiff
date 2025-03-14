import typer

import tcf_to_ometiff

main = typer.Typer()


@main.command()
def parse_multiple(top_folder: str, config_file_path: str, output_xml: bool = False, include_mip: bool = True):
    """CLI to parse images stored in subfolders of a top folder. This is the
    standard TomoStudio case when on each date a new top folder is created that
    has one subfolder for each snapshot. The parsed OME-TIFF images are stored
    in the respective sub folders.

    :param top_folder: Relative or absolute file path to top folder
    :param config_file_path: Relative or absolute file path to csv file with project OMERO metadata
    :param output_xml: If True, output the ome-xml files alongside the ome-tiff files
    :param include_mip: If True, maximum intensity projections are included in the output ome tiff files

    """
    tcf_to_ometiff.transform_folder(top_folder, config_file_path, output_xml, include_mip)


@main.command()
def parse(folder: str, config_file_path: str, output_xml: bool = False, include_mip: bool = True):
    """CLI to parse an image in a folder that has the same name as the folder and
    additionally ends with .TCF. The parsed OME-TIFF image is stored in the
    same folder.

    :param folder: Relative or absolute file path to folder containing image
    :param config_file_path: Relative or absolute file path to csv file with project OMERO metadata
    :param output_xml: If True, output the ome-xml file alongside the ome-tiff file
    :param include_mip: If True, maximum intensity projections are included in the output ome tiff file

    """
    overall_md = tcf_to_ometiff.create_overall_config(config_file_path)
    tcf_to_ometiff.transform_tcf(folder, overall_md, output_xml, include_mip)


if __name__ == "__main__":
    main()
