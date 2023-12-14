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


def def_mic(sn, mic_model, lot=None):
    """Create ome-types microscope for use in OME-XML

    :param mic_model: model of the microscope
    :param sn: str: serial number of the microscope
    :param lot:  Lot of the microscope
    :return: ome-types microscope
    """
    return model.Microscope(
        manufacturer="Tomocube Inc.",
        model=mic_model,
        serial_number=sn,
        lot_number=lot,
        type="Other",
    )


def def_det(det_id):
    """Create ome-types detector for use in OME-XML

    :param det_id: str: ID of the detector
    :return: ome-types detector
    """
    return model.Detector(id=det_id, type="CMOS")


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

    if light_source_id == "LightSource:0":
        return model.Laser(
            id=light_source_id,
            power=0.05,
            tuneable=False,
            type="SolidState",
            wavelength=532,
        )

    else:
        return model.LightEmittingDiode(
            id=light_source_id
        )


def def_instr(instr_id, microscope, detectors, lasers, leds):
    """Create ome-types instrument for use in OME-XML

    :param instr_id: str: ID of the instrument
    :param microscope: ome_types.model.Microscope
    :param detectors: list of ome_types.model.Detector
    :param lasers: list of ome_types.model.Laser
    :param leds: list of ome_types.model.LightEmittingDiode
    :return: ome-types instrument
    """

    return model.Instrument(
        id=instr_id,
        microscope=microscope,
        detectors=detectors,
        lasers=lasers,
        light_emitting_diodes=leds
    )


def def_channel(image_name, img_md=None):
    """Create ome-types channel for use in OME-XML

    :param
    :return: ome-types channel with "Phase" as contrast method
    """

    if image_name == "ht":
        return model.Channel(
            id="Channel:0",
            acquisition_mode="Other",
            contrast_method="Phase",
            illumination_type="Transmitted",
            name="Holotomography",
            light_source_settings=model.LightSourceSettings(
                id="LightSource:0",
                wavelength=532
            ),
            samples_per_pixel=1,
        )

    elif image_name == "bf":
        return model.Channel(
            id="Channel:1",
            acquisition_mode="BrightField",
            contrast_method="Brightfield",
            illumination_type="Transmitted",
            name="Brightfield",
            light_source_settings=model.LightSourceSettings(
                id="LightSource:0",
                wavelength=532
            ),
            samples_per_pixel=1,
        )

    else:
        lambda_emi = img_md["FLCH{}_Fluorophore_Emission".format(image_name[2])]
        fluor = img_md["FLCH{}_Fluorophore_Name".format(image_name[2])]

        if image_name[2] == "0":
            color = "blue"
            lambda_exc = 385
            settings = model.LightSourceSettings(
                id="LightSource:1",
                wavelength=lambda_exc
            )
        elif image_name[2] == "1":
            color = "green"
            lambda_exc = 470
            settings = model.LightSourceSettings(
                id="LightSource:2",
                wavelength=lambda_exc
            )
        elif image_name[2] == "2":
            color = "red"
            lambda_exc = 570
            settings = model.LightSourceSettings(
                id="LightSource:3",
                wavelength=lambda_exc
            )
        else:
            print("Unknown image name: {}".format(image_name))
        return model.Channel(
            id="Channel:{}".format(int(image_name[2])+2),
            acquisition_mode="Other",
            contrast_method="Fluorescence",
            illumination_type="Transmitted",
            name="Fluorescence {}".format(color),
            light_source_settings=settings,
            samples_per_pixel=1,
            color=color,
            excitation_wavelength=lambda_exc,
            emission_wavelength=lambda_emi,
            fluor=fluor
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
    return model.Experiment(description=desc, experimenter_ref=exper)


def def_project(proj_id, proj_name, desc):
    """Create ome-types project for use in OME-XML

    :param proj_id: str: ID of the project
    :param proj_name: str: name of the project
    :param desc: str: description of the project
    :return: ome-types project
    """
    return model.Project(id=proj_id, name=proj_name, description=desc)


def def_annotations(img_metadata):
    """Create ome-types StructuredAnnotations with additional per-image metadata.

    :param img_metadata: Dict with all per-image metadata
    :return: ome-types StructuredAnnotations object
    """
    ann_overall = model.MapAnnotation(
        id="Annotation:0",
        description="Overall metadata for recording and setup",
        value=model.Map(ms=[
                {"value": img_metadata["Medium_Name"], "k": "MediumName"},
                {"value": img_metadata["Medium_RI"], "k": "MediumRI"},
                {"value": img_metadata["Immersion_RI"], "k": "ImmersionRI"},
                {"value": img_metadata["Annotation"], "k": "Annotation"},
                {"value": img_metadata["SW Version"], "k": "TomoStudioVersion"}
        ])
    )

    if int(img_metadata["Images HT3D"]) > 0 or int(img_metadata["Images HT2D"]) > 0:
        ann_ht = model.MapAnnotation(
            id="Annotation:1",
            description="Additional metadata for HT and Phase images",
            value=model.Map(ms=[
                    {"value": img_metadata["mapping sign"], "k": "HT_MappingSign"},
                    {"value": img_metadata["phase sign"], "k": "HT_PhaseSign"},
                    {"value": img_metadata["iteration"], "k": "HT_Iterations"},
                    {"value": img_metadata["Camera Shutter"], "k": "HT_ExposureTime"},
                    {"value": img_metadata["Camera Gain"], "k": "HT_Gain"}
            ])
        )
    else:
        ann_ht = None

    if int(img_metadata["Images BF"]) > 0:
        ann_bf = model.MapAnnotation(
            id="Annotation:2",
            description="Additional metadata for brightfield image",
            value=model.Map(ms=[
                    {"value": img_metadata["BF_Camera_Shutter"], "k": "BF_ExposureTime"},
                    {"value": img_metadata["BF_Light_Intensity"], "k": "BF_Intensity"}
            ])
        )
    else:
        ann_bf = None

    if int(img_metadata["Images FL3D"]) > 0:
        ann_fl = []
        colors_dict = {0: "blue", 1: "green", 2: "red"}
        for i in range(3):
            if img_metadata["FLCH{}_Enable".format(i)] == "true":
                ann_fl.append(
                    model.MapAnnotation(
                        id="Annotation:{}".format(i+3),
                        description="Additional metadata for Fluorescence Channel {} images".format(colors_dict[i]),
                        value=model.Map(ms=[
                            {
                                "value": img_metadata["FLCH{}_Camera_Shutter".format(i)],
                                "k": "FL{}_ExposureTime".format(i)
                            }, {
                                "value": img_metadata["FLCH{}_Camera_Gain".format(i)],
                                "k": "FL{}_Gain".format(i)
                            }, {
                                "value":  img_metadata["FLCH{}_Light_Intensity".format(i)],
                                "k": "FL{}_Intensity".format(i)
                            }
                        ])
                    )
                )
    else:
        ann_fl = None

    anns_list = [item for item in [ann_overall, ann_ht, ann_bf] + ann_fl if item]
    anns = model.StructuredAnnotationList(__root__=anns_list)

    return anns


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
    ann_id
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
    :param ann_id: ID of annotation with additional image metadata
    :return: ome-types image with relevant metadata
    :return: int to give the image plane offset for the next image in a multidimensional array
    (with t and channel components)
    """
    try:
        len_z = data_use.attrs["SizeZ"][0]
        physical_size_z = round(data_use.attrs["ResolutionZ"][0], 2)
    except KeyError:
        len_z = 1
        physical_size_z = None
    len_t = data_use.attrs["DataCount"][0]
    len_c = 1
    n_planes = len_z * len_t * len_c

    tiffdata = [model.TiffData(plane_count=n_planes, ifd=offset)]

    pixels = model.Pixels(
        dimension_order="XYZTC",
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
        experiment_ref=model.ExperimentRef(id=experiment.id),
        experimenter_ref=model.ExperimenterRef(id=experimenter.id),
        instrument_ref=model.InstrumentRef(id=instrument.id),
        annotation_refs=[model.AnnotationRef(id=ann_id)]
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
    config_dat = [item.split(",", 1) for item in config_dat if item != "\n"]
    config_dict = {item[0]: item[1].strip("\n") for item in config_dat}
    return config_dict


def def_omero_overall_md(config_dict):
    """Create experimenter, experiment and project metadata dictionaries needed to
create the OME-TIFF from user-provided metadata.

    :param config_dict: Dict of user-created metadata
    :return: Dict containing metadata needed for OME-TIFF

    """

    overall_metadata = dict()
    overall_metadata["exper"] = def_experimenter(
        config_dict["exper_id"],
        config_dict["exper_email"],
        config_dict["exper_inst"],
        config_dict["exper_firstn"],
        config_dict["exper_lastn"],
        config_dict["exper_usern"],
    )
    overall_metadata["proj"] = def_project(
        config_dict["proj_id"], config_dict["proj_name"], config_dict["proj_desc"]
    )
    return overall_metadata


def create_overall_config(overall_config_path):
    """Create dict with overall metadata that contains both the raw metadata read
from the user-provided file and metadata created from it that is needed
to create the OME-TIFF.

    :param overall_config_path: Path of csv file with metadata
    :return: Dict containing the overall metadata that can be used for all folders in one top folder

    """
    overall_config_dict = read_overall_config(overall_config_path)
    omero_overall_md = def_omero_overall_md(overall_config_dict)
    overall_md = dict(overall_config_dict, **omero_overall_md)
    return overall_md


def read_image_config(folder):
    """Read auto-generated files with config data from image folder (config.dat and JobParameter.tcp) and return dict.

    :param folder: Folder name as string
    :return: Dict containing the per-image metadata
    """

    # read and treat config.dat
    with open(join(folder, "config.dat")) as f:
        exp_config_dat_1 = f.readlines()

    for i in range(len(exp_config_dat_1)):  # output lacks a ","
        if exp_config_dat_1[i].startswith("Immersion_RI"):
            exp_config_dat_1[i] = "Immersion_RI," + exp_config_dat_1[i][12:]
            break

    exp_config_dat_1 = [item.rstrip("\n").split(",", 1) for item in exp_config_dat_1 if item != "\n"]

    # read and treat JobParameter.tcp
    with open(join(folder, "JobParameter.tcp")) as f:
        exp_config_dat_2 = f.readlines()[1:]

    exp_config_dat_2 = [item.rstrip("\n").split("=", 1) for item in exp_config_dat_2 if item != "\n"]

    # print(*exp_config_dat_1, sep="\n")
    # print(*exp_config_dat_2, sep="\n")
    # merge
    exp_config_dict = {item[0]: item[1] for item in exp_config_dat_1}
    exp_config_dict.update({item[0]: item[1] for item in exp_config_dat_2})

    return exp_config_dict


def define_image_metadata(overall_config_dict, img_config_dict):
    """Integrate project and image metadata to obtain comprehensive metadata dict
used to create the OME-TIFF.

    :param overall_config_dict: Dict with overall metadata given by the user
    :param img_config_dict: Dict with per-image metadata extracted from config file in image folder
    :returns: Dict containing all metadata to create the OME-TIFF.

    """
    img_metadata = dict()
    img_metadata["exp"] = def_experiment(
        img_config_dict["Job_Title"], model.ExperimenterRef(id=overall_config_dict["exper_id"])
    )
    img_metadata["mic"] = def_mic(
        img_config_dict["Serial"], overall_config_dict["mic_model"], overall_config_dict["mic_lot"]
    )
    img_metadata["det"] = [def_det(overall_config_dict["det_id"])]
    img_metadata["obj"] = def_obj(
        overall_config_dict["obj_id"],
        img_config_dict["NA"],
        img_config_dict["M"]
    )
    img_metadata["lasers"] = [def_light_source(overall_config_dict["light_source_id_ht"])]
    img_metadata["leds"] = [
        def_light_source(overall_config_dict["light_source_id_fl0"]),
        def_light_source(overall_config_dict["light_source_id_fl1"]),
        def_light_source(overall_config_dict["light_source_id_fl2"])
    ]
    img_metadata["instr"] = def_instr(
        overall_config_dict["instr_id"],
        img_metadata["mic"],
        img_metadata["det"],
        img_metadata["lasers"],
        img_metadata["leds"]
    )
    img_metadata["channel_ht"] = def_channel("ht")
    img_metadata["channel_bf"] = def_channel("bf")
    img_metadata["channel_fl0"] = def_channel("fl0", img_config_dict)
    img_metadata["channel_fl1"] = def_channel("fl1", img_config_dict)
    img_metadata["channel_fl2"] = def_channel("fl2", img_config_dict)

    img_metadata["anns"] = def_annotations(img_config_dict)

    return img_metadata


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
    # timestamp = get_img_timestamp(folder)

    # open HDF5 image (TCF)
    logging.info("Reading image")
    dat = h5py.File(join(folder, basename(folder) + ".TCF"), "r")
    # file_name_store = join(top_folder, folder, folder + ".ome.tiff")
    file_name_store = join(folder, basename(folder) + ".ome.tiff")
    img_ome_xmls = []
    imgs = []
    plane_offset = 0  # for multiple timesteps / channels

    keys_to_loop = list(dat["Data"].keys())
    # FL channels are nested one level below imaging modalities --> (ugly) trick to achieve them in a similar way
    if "2DFLMIP" in keys_to_loop:
        n_chans = len(dat["Data"]["2DFLMIP"])
        keys_to_loop.extend((n_chans-1)*["2DFLMIP"])
        fl_mip_counter = 0
    if "3DFL" in keys_to_loop:
        n_chans = len(dat["Data"]["3DFL"])
        keys_to_loop.extend((n_chans-1)*["3DFL"])
        fl_3d_counter = 0

    for name in keys_to_loop:
        logging.info("Working on {}".format(name))
        data_use = dat["Data"][name]

        if name == "2DMIP":
            channels = [img_md["channel_ht"]]
            description = "2D Holotomography Maximum Intensity Projection"
            data_type = "uint16"
            img_formatted = np.array(
                [data_use[item][()][np.newaxis] for item in data_use]
            )[np.newaxis]
            ann_ref = 1
            timestamp = data_use["000000"].attrs["RecordingTime"][0].decode("utf-8")

        elif name == "2D":
            channels = [img_md["channel_ht"]]
            description = "2D Phasemap"
            data_type = "float"
            img_formatted = np.array([data_use[item][()] for item in data_use])[
                np.newaxis
            ]
            ann_ref = 1
            timestamp = data_use["000000"].attrs["RecordingTime"][0].decode("utf-8")

        elif name == "BF":
            channels = [img_md["channel_bf"]]
            description = "2D Brightfield"
            data_type = "uint8"
            img_formatted = np.array([data_use[item][0] for item in data_use])[
                np.newaxis
            ]
            ann_ref = 2
            timestamp = data_use["000000"].attrs["RecordingTime"][0].decode("utf-8")

        elif name == "3D":
            channels = [img_md["channel_ht"]]
            description = "3D Holotomography"
            data_type = "uint16"
            img_formatted = np.array([data_use[item][()] for item in data_use])[
                np.newaxis
            ]
            ann_ref = 1
            timestamp = data_use["000000"].attrs["RecordingTime"][0].decode("utf-8")

        elif name == "2DFLMIP":
            channel = list(data_use.keys())[fl_mip_counter]
            fl_mip_counter += 1

            channels = [img_md["channel_fl{}".format(channel[2])]]
            description = "2D {} Maximum Intensity Projection"\
                .format(img_md["channel_fl{}".format(channel[2])].name)
            data_type = "uint16"
            img_formatted = np.array(
                [data_use[channel][item][()][np.newaxis] for item in data_use[channel]]
            )[np.newaxis]
            ann_ref = 3 + int(channel[2])
            timestamp = data_use[channel]["000000"].attrs["RecordingTime"][0].decode("utf-8")

        elif name == "3DFL":
            channel = list(data_use.keys())[fl_3d_counter]
            fl_3d_counter += 1

            channels = [img_md["channel_fl{}".format(channel[2])]]
            description = "3D {}".format(img_md["channel_fl{}".format(channel[2])].name)
            data_type = "uint16"
            img_formatted = np.array([data_use[channel][item][()] for item in data_use[channel]])[
                np.newaxis
            ]
            ann_ref = 3 + int(channel[2])
            timestamp = data_use[channel]["000000"].attrs["RecordingTime"][0].decode("utf-8")

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
                img_md["exp"],
                overall_md["exper"],
                img_md["instr"],
                data_type,
                "Annotation:{}".format(ann_ref)
            )
        except Exception as e:
            raise Exception("Exception during xml building: {}".format(e))

        img_ome_xmls.append(xml)
        imgs.append(img_formatted)

    ome_xmls = model.OME(
        creator="tcf_to_ome by Henning Zwirnmann v0.4",
        images=img_ome_xmls,
        experiments=[img_md["exp"]],
        experimenters=[overall_md["exper"]],
        instruments=[img_md["instr"]],
        structured_annotations=img_md["anns"]
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

    :param top_folder: Relative or absolute file path to folder containing image
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
