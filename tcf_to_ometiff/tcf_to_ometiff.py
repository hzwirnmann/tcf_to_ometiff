from os.path import join, basename, isdir
from os import listdir

import numpy as np
import logging

from ome_types import model
import h5py
from aicsimageio import writers

logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)


def def_mic(mic_id, sn, lot=None):
    """Create ome-types microscope for use in OME-XML

    :param mic_id: str: ID of the microscope
    :param sn: str: serial number of the microscope
    :return: ome-types microscope
    """
    return model.Microscope(
        id=mic_id,
        manufacturer="Tomocube Inc.",
        model="HT-2H",
        serial_number=sn,
        lot_number=lot,
        type="Other",
    )


def def_det(det_id):
    """Create ome-types detector for use in OME-XML

    :param det_id: str: ID of the detector
    :return: ome-types detector
    """
    return model.Detector(id=det_id, type="CCD")


def def_obj(obj_id, lens_na, lens_magn):
    """Create ome-types objective for use in OME-XML

    :param obj_id: str: ID of the objective
    :param lens_na: float: numerical aperture
    :param lens_magn: float: magnification
    :return: ome-types objective
    """
    return model.Objective(
        id=obj_id, lens_na=lens_na, nominal_magnification=lens_magn, immersion="Water"
    )


def def_light_source(light_source_id):
    """Create ome-types light source (HT laser) for use in OME-XML

    :param light_source_id: str: ID of the light source
    :return: ome-types laser
    """

    return model.Laser(
        id=light_source_id,
        power=0.05,
        tuneable=False,
        type="SolidState",
        wavelength=532,
    )


def def_instr(instr_id, microscope, detectors, light_sources):
    """Create ome-types instrument for use in OME-XML

    :param instr_id: str: ID of the instrument
    :param microscope: ome_types.model.microscope
    :param detectors: list of ome_types.model.detector
    :param light_sources: list of ome_types.model.light_source
    :return: ome-types instrument
    """

    return model.Instrument(
        id=instr_id,
        microscope=microscope,
        detectors=detectors,
        light_source_group=light_sources,
    )


def def_channel(chan_id, ls_id, chan_name):
    """Create ome-types channel for use in OME-XML

    :param chan_id: str: ID of the channel
    :param ls_id: id of light source used
    :param chan_name: str: channel name
    :return: ome-types channel with "Phase" as contrast method
    """
    return model.Channel(
        id=chan_id,
        acquisition_mode="Other",
        contrast_method="Phase",
        illumination_type="Other",
        name=chan_name,
        light_source_settings=model.LightSourceSettings(id=ls_id),
        samples_per_pixel=1,
    )


def def_experimenter(exper_id, email, inst, first_name, last_name, user_name):
    """Create ome-types experimenter for use in OME-XML

    :param exper_id: str: ID of the experimenter
    :param email: str: email address of the experimenter
    :param inst: str: institution of the experimenter
    :param first_name: str: first name of the experimenter
    :param last_name: str: last name of the experimenter
    :param user_name: str: user name of the experimenter
    :return: ome-types experimenter
    """
    return model.Experimenter(
        id=exper_id,
        email=email,
        institution=inst,
        first_name=first_name,
        last_name=last_name,
        user_name=user_name,
    )


def def_experiment(desc, exper):
    """Create ome-types experiment for use in OME-XML

    :param desc: str: experiment description
    :param exper: ome-types.model.experimenter
    :return: ome-types experiment
    """
    return model.Experiment(description=desc, experimenter=exper)


def def_project(proj_id, proj_name, desc):
    """Create ome-types project for use in OME-XML

    :param proj_id: str: ID of the project
    :param proj_name: str: name of the project
    :param desc: str: description of the project
    :return: ome-types project
    """
    return model.Project(id=proj_id, name=proj_name, description=desc)


def build_ome_xml(
    data_use,
    offset,
    channels,
    timestamp,
    description,
    experiment,
    experimenter,
    instrument,
    data_type,
):
    """Create OME-XML file from given ome-types metadata

    :param data_use:
    :param offset: int: plane offset
    :param channels: ome-types channels used in image
    :param timestamp: str: timestamp in YYYY-MM-DD format the image was acquired at
    :param description: ome-types description of the image
    :param experiment: ome-types experiment the image was part of
    :param experimenter: ome-types experimenter who took the image
    :param instrument: ome-types instrument the image was taken with
    :param data_type: Python data type of the image data
    :return: ome-types image with relevant metadata
    :return: int to give the image plane offset for the next image in a multidimensional array (with t and channel components)
    """
    try:
        len_z = data_use.attrs["SizeZ"][0]
        physical_size_z = round(data_use.attrs["ResolutionZ"][0], 2)
    except KeyError:
        len_z = 1
        physical_size_z = None
    len_t = data_use.attrs["DataCount"][0]
    try:
        len_c = data_use.attrs["Channels"][0]
    except KeyError:
        len_c = 1
    n_planes = len_z * len_t * len_c

    tiffdata = [model.TiffData(plane_count=n_planes, ifd=offset)]

    pixels = model.Pixels(
        dimension_order=("XYZTC"),
        size_c=len_c,
        size_t=len_t,
        size_x=data_use.attrs["SizeX"][0],
        size_y=data_use.attrs["SizeY"][0],
        size_z=len_z,
        type=data_type,
        physical_size_x=round(data_use.attrs["ResolutionX"][0], 2),
        physical_size_y=round(data_use.attrs["ResolutionY"][0], 2),
        physical_size_z=physical_size_z,
        tiff_data_blocks=tiffdata,
        time_increment=data_use.attrs["TimeInterval"][0],
        channels=channels,
    )

    image = model.Image(
        pixels=pixels,
        acquisition_date=timestamp,
        name=description,
        description=description,
        experiment_ref=experiment,
        experimenter_ref=experimenter,
        instrument_ref=instrument,
    )

    return image, offset + n_planes


def read_overall_config(filepath):
    """Read user-created file with metadata needed to create the OME-TIFF.

    :param filepath: Path of csv file with metadata
    :return: Dict containing the overall metadata
    """

    logging.info("Reading overall config from {}".format(filepath))
    with open(filepath) as f:
        config_dat = f.readlines()
    config_dat = [item.split(",", 1) for item in config_dat]
    config_dict = {item[0]: item[1].strip("\n") for item in config_dat}
    return config_dict


def def_omero_overall_md(config_dict):
    """Create experimenter, experiment and project metadata dictionaries needed to
create the OME-TIFF from user-provided metadata.

    :param config_dict: Dict of user-created metadata
    :return: Dict containing metadata needed for OME-TIFF

    """

    overall_metadata = {}
    overall_metadata["exper"] = def_experimenter(
        config_dict["exper_id"],
        config_dict["exper_email"],
        config_dict["exper_inst"],
        config_dict["exper_firstn"],
        config_dict["exper_lastn"],
        config_dict["exper_usern"],
    )
    overall_metadata["exp"] = def_experiment(
        config_dict["exp_desc"], config_dict["exper_id"]
    )
    overall_metadata["proj"] = def_project(
        config_dict["proj_id"], config_dict["proj_name"], config_dict["proj_desc"]
    )
    return overall_metadata


def create_overall_config(overall_config_path):
    """Create dict with overall metadata that contains both the raw metadata read
from the user-provided file as well as metadata created from it that is needed
to create the OME-TIFF.

    :param overall_config_path: Path of csv file with metadata
    :return: Dict containing the overall metadata that can be used for all folders in one top folder

    """
    overall_config_dict = read_overall_config(overall_config_path)
    omero_overall_md = def_omero_overall_md(overall_config_dict)
    overall_md = dict(overall_config_dict, **omero_overall_md)
    return overall_md


def read_image_config(folder):
    """Read file with config data from image folder and return dict.

    :param folder: Folder name as string
    :return: Dict containing the per-image metadata
    """

    with open(join(folder, "config.dat")) as f:
        exp_config_dat = f.readlines()

    for i in range(len(exp_config_dat)):  # buggy software output lacks a ","
        if exp_config_dat[i].startswith("Immersion_RI"):
            exp_config_dat[i] = "Immersion_RI," + exp_config_dat[i][12:]
            break

    exp_config_dat = [item.split(",", 1) for item in exp_config_dat if item != "\n"]
    exp_config_dict = {item[0]: item[1].strip("\n") for item in exp_config_dat}

    return exp_config_dict


def define_image_metadata(config_dict, exp_config_dict):
    """Integrate project and image metadata to obtain comprehensive metadata dict
used to create the OME-TIFF.

    :param config_dict: Metadata dict with metadata given by the user
    :param exp_config_dict: Metadata dict with metadata extracted config file in image folder
    :returns: dict containing all metadata to create the OME-TIFF.

    """
    img_metadata = {}
    img_metadata["mic"] = def_mic(
        config_dict["mic_id"], exp_config_dict["Serial"], config_dict["lot"]
    )
    img_metadata["det"] = def_det(config_dict["det_id"])
    img_metadata["obj"] = def_obj(
        config_dict["obj_id"],
        exp_config_dict["NA"],
        exp_config_dict["M"]
    )
    img_metadata["light_source"] = def_light_source(config_dict["light_source_id"])
    img_metadata["instr"] = def_instr(
        config_dict["instr_id"],
        img_metadata["mic"],
        [img_metadata["det"]],
        [img_metadata["light_source"]],
    )
    img_metadata["channel_ht_3d"] = def_channel(
        config_dict["channel_id_ht3d"], config_dict["light_source_id"], "3D HT"
    )
    img_metadata["channel_ht_2d"] = def_channel(
        config_dict["channel_id_ht2d"], config_dict["light_source_id"], "2D MIP HT"
    )
    img_metadata["channel_ht_phase"] = def_channel(
        config_dict["channel_id_htphase"], config_dict["light_source_id"], "2D Phase"
    )

    return img_metadata


def get_img_timestamp(folder):
    """
    Extract timestamp from timestamp file

    :param folder: Relative or absolute file path to folder containing image and timestamp file
    :returns: timestamp str in format "YYYY-MM-DDTHH:MM:SS"
    """
    # Get image timestamp
    with open(join(folder, "timestamp.txt")) as f:
        timestamp_long = f.read()
        timestamp = (
            timestamp_long[:4]
            + "-"
            + timestamp_long[4:6]
            + "-"
            + timestamp_long[6:8]
            + "T"
            + timestamp_long[8:10]
            + ":"
            + timestamp_long[10:12]
            + ":"
            + timestamp_long[12:14]
        )
    return timestamp


def transform_tcf(folder, overall_md):
    """Parse an image in a folder that has the same name as the folder
    and additionally ends with .TCF. The parsed OME-TIFF image is stored in the
    same folder. It loops over all imaging modalities contained in the TCF H5F
    file and transforms them into suitable numpy arrays. Relevant metadata is
    taken both from the config file passed by the user as well as from the .TCF
    file.

    :param folder: Relative or absolute file path to folder containing image
    :param overall_md: Overall metadata dict

    """

    folder = folder.rstrip("/")
    try:
        exp_config_dict = read_image_config(folder)
    except Exception as e:
        raise Exception("Skipping folder {} with Exception {}".format(folder, e))

    img_md = define_image_metadata(overall_md, exp_config_dict)
    timestamp = get_img_timestamp(folder)

    # open HDF5 image (TCF)
    logging.info("Reading image")
    dat = h5py.File(join(folder, basename(folder) + ".TCF"), "r")
    # file_name_store = join(top_folder, folder, folder + ".ome.tiff")
    file_name_store = join(folder, basename(folder) + ".ome.tiff")
    img_ome_xmls = []
    imgs = []
    plane_offset = 0  # for multiple timesteps / channels
    for name in dat["Data"].keys():
        data_use = dat["Data"][name]
        logging.info("Working on {}".format(name))
        if name == "2DMIP":
            channels = [img_md["channel_ht_2d"]]
            description = "2D Holotomography Maximum Intensity Projection"
            data_type = "uint16"
            img_formatted = np.array(
                [data_use[item][()][np.newaxis] for item in data_use]
            )[np.newaxis]
        elif name == "2D":
            channels = [img_md["channel_ht_phase"]]
            description = "2D Phasemap"
            data_type = "float"
            img_formatted = np.array([data_use[item][()] for item in data_use])[
                np.newaxis
            ]
        # elif name == "BF":
        #     channels = [XXX]
        #     description = "2D Brightfield"
        #     img_formatted = XXX
        elif name == "3D":
            channels = [img_md["channel_ht_3d"]]
            description = "3D Holotomography"
            data_type = "uint16"
            img_formatted = np.array([data_use[item][()] for item in data_use])[
                np.newaxis
            ]
        else:
            logging.info("Skipping unknown data type {}".format(name))
            continue
        # print("No valid data type in {}: {}".format(folder, name))
        # sys.exit(-1)

        try:
            xml, plane_offset = build_ome_xml(
                data_use,
                plane_offset,
                channels,
                timestamp,
                description,
                overall_md["exp"],
                overall_md["exper"],
                img_md["instr"],
                data_type,
            )
        except Exception as e:
            raise Exception("Exception during xml building: {}".format(e))

        img_ome_xmls.append(xml)
        imgs.append(img_formatted)

    ome_xmls = model.OME(
        creator="tcf_to_ome by Henning Zwirnmann v0.1",
        images=img_ome_xmls,
        experiments=[overall_md["exp"]],
        experimenters=[overall_md["exper"]],
        instruments=[img_md["instr"]],
    )

    logging.info("Writing file {}".format(file_name_store))
    writers.ome_tiff_writer.OmeTiffWriter().save(
        imgs,
        file_name_store,
        ome_xml=ome_xmls,
    )


def transform_folder(top_folder, overall_config_path):
    """Parse images stored in subfolders of a top folder. This is the
    standard TomoStudio case when on each date a new top folder is created that
    has one subfolder for each snapshot. The parsed OME-TIFF images are stored
    in the respective subfolders.

    :param folder: Relative or absolute file path to folder containing image
    :param overall_config_path: Relative or absolute file path to csv file with overall metadata

    """
    overall_md = create_overall_config(overall_config_path)

    logging.info("Traversing folders in {}".format(top_folder))
    folders = [d for d in listdir(top_folder) if isdir(join(top_folder, d))]
    for folder in folders:
        logging.info("Reading folder {}".format(folder))
        try:
            transform_tcf(join(top_folder, folder), overall_md)
        except Exception as e:
            logging.info(e)
            continue
