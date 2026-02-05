from os.path import join, basename, isdir
from os import listdir
from datetime import datetime

import numpy as np
import logging

from ome_types import model
import h5py
from bioio_ome_tiff.writers import OmeTiffWriter


from .version import __version__

logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)


def def_mic(sn, mic_model, lot=None):
    """Create ome-types Microscope for use in OME-XML.

    :param mic_model: model of the microscope
    :param sn: str: serial number of the microscope
    :param lot:  Lot of the microscope
    :return: ome-types Microscope
    """
    return model.Microscope(
        manufacturer="Tomocube Inc.",
        model=mic_model,
        serial_number=sn,
        lot_number=lot,
        type="Other",
    )


def def_det(det_id):
    """Create ome-types Detector for use in OME-XML.

    :param det_id: str: ID of the detector
    :return: ome-types Detector
    """
    return model.Detector(id=det_id, type="CMOS")


def def_obj(obj_id, lens_na, lens_magn):
    """Create ome-types Objective for use in OME-XML.

    :param obj_id: str: ID of the objective
    :param lens_na: float: numerical aperture
    :param lens_magn: float: magnification
    :return: ome-types Objective
    """
    return model.Objective(
        id=obj_id, lens_na=lens_na, nominal_magnification=lens_magn, immersion="Water"
    )


def def_light_source(light_source_id):
    """Create ome-types LightSource (HT laser / FL LED) for use in OME-XML.

    :param light_source_id: str: ID of the light source
    :return: ome-types LightSource (Laser or LightEmittingDiode)
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
    """Create ome-types Instrument for use in OME-XML.

    :param instr_id: str: ID of the instrument
    :param microscope: ome_types.model.Microscope
    :param detectors: list of ome_types.model.Detector
    :param lasers: list of ome_types.model.Laser
    :param leds: list of ome_types.model.LightEmittingDiode
    :return: ome-types Instrument
    """

    return model.Instrument(
        id=instr_id,
        microscope=microscope,
        detectors=detectors,
        lasers=lasers,
        light_emitting_diodes=leds
    )


def def_ht_fl_shift_stagelabel(offset, fl_height):
    """Create ome-types StageLabel to define the z shift between ht and fl image.

    :param
    :return: ome-types StageLabel
    """
    z_shift = np.round(offset - fl_height/2, 2)

    sl = model.StageLabel(
        name="Fluorescence Image Z Shift",
        z=z_shift,
        z_unit="mm"
        # x=x_stage,
        # x_unit="mm",
        # y=y_stage,
        # y_unit="mm"
    )

    return sl


def def_channel(image_name, img_md=None):
    """Create ome-types Channel for either HT or FL for use in OME-XML.

    :param
    :return: ome-types Channel
    """

    if image_name == "ht":
        return model.Channel(
            # id="Channel:0",
            acquisition_mode="Other",
            contrast_method="Phase",  # not correct actually, contrast is rather refractive index
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
            # id="Channel:1",
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
            color = "#0000FFFF"
            lambda_exc = 385
            settings = model.LightSourceSettings(
                id="LightSource:1",
                wavelength=lambda_exc
            )
        elif image_name[2] == "1":
            color = "#008000FF"
            lambda_exc = 470
            settings = model.LightSourceSettings(
                id="LightSource:2",
                wavelength=lambda_exc
            )
        elif image_name[2] == "2":
            color = "#FF0000FF"
            lambda_exc = 570
            settings = model.LightSourceSettings(
                id="LightSource:3",
                wavelength=lambda_exc
            )
        else:
            logging.warning("Unknown image name: {}".format(image_name))
        return model.Channel(
            # id="Channel:{}".format(int(image_name[2])+2),
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
    """Create ome-types Experimenter for use in OME-XML.

    :param exper_id: str: ID of the experimenter
    :param email: str: email address of the experimenter
    :param inst: str: institution of the experimenter
    :param first_name: str: first name of the experimenter
    :param last_name: str: last name of the experimenter
    :param user_name: str: username of the experimenter
    :return: ome-types Experimenter
    """
    return model.Experimenter(
        id=exper_id,
        email=email,
        institution=inst,
        first_name=first_name,
        last_name=last_name,
        user_name=user_name,
    )


def def_experimenter_group(eg_id, desc, exper_refs, leaders, name):

    """Create ome-types ExperimenterGroup for use in OME-XML.

    :param eg_id: str: ID of the experimenter group
    :param desc: str: Description of the experimenter group
    :param exper_refs: list of ome-types ExperimenterRefs for experimenters in the group
    :param leaders: list of ome-types Leaders of the group
    :param name: str: name of the experimenter group
    :return: ome-types ExperimenterGroup
    """
    return model.ExperimenterGroup(
        id=eg_id,
        name=name,
        leaders=leaders,
        experimenter_refs=exper_refs,
        description=desc
    )


def def_experiment(desc, exper, exp_type=None):
    """Create ome-types Experiment for use in OME-XML.

    :param desc: str: experiment description
    :param exper: ome-types Experimenter
    :param exp_type: list of valid str for experiment type
    :return: ome-types Experiment
    """
    if not exp_type:
        exp_type = ["Other"]
    return model.Experiment(description=desc, experimenter_ref=exper, type=exp_type)


def def_project(proj_id, proj_name, desc):
    """Create ome-types Project for use in OME-XML.

    :param proj_id: str: ID of the project
    :param proj_name: str: name of the project
    :param desc: str: description of the project
    :return: ome-types Project
    """
    return model.Project(id=proj_id, name=proj_name, description=desc)


def def_annotations(img_metadata, tiling_info):
    """Create ome-types StructuredAnnotations with additional per-image metadata.

    :param img_metadata: Dict with all per-image metadata
    :param tiling_info: Dict with information about tiles (could be empty)
    :return: ome-types StructuredAnnotations object
    """

    anns = []
    ann_overall = model.MapAnnotation(
        id="Annotation:0",
        namespace="overall",
        description="Overall metadata for recording and setup",
        value=model.Map(ms=[
                {"value": img_metadata["Medium_Name"], "k": "MediumName"},
                {"value": img_metadata["Medium_RI"], "k": "MediumRI"},
                {"value": img_metadata["Immersion_RI"], "k": "ImmersionRI"},
                {"value": img_metadata["Annotation"], "k": "Annotation"},
                {"value": img_metadata["SW Version"], "k": "TomoStudioVersion"},
                {"value": img_metadata["Job_Title"], "k": "ImageJobTitle"}
        ])
    )
    anns.append(ann_overall)

    # backwards compatibility: old TomoStudio versions do not add number of images to config.dat, so we assume that
    # HT and FL images are available and add the annotations; however not for BF because there is no BF information
    # in the metadata files
    if "Images HT3D" not in img_metadata or int(img_metadata["Images HT3D"]) > 0 \
            or int(img_metadata["Images HT2D"]) > 0:
        ann_ht = model.MapAnnotation(
            id="Annotation:1",
            namespace="holotomography",
            description="Additional metadata for HT and Phase images",
            value=model.Map(ms=[
                    {"value": img_metadata["mapping sign"], "k": "HT_MappingSign"},
                    {"value": img_metadata["phase sign"], "k": "HT_PhaseSign"},
                    {"value": img_metadata["iteration"], "k": "HT_Iterations"},
                    {"value": img_metadata["Camera Shutter"], "k": "HT_ExposureTime"},
                    {"value": img_metadata["Camera Gain"], "k": "HT_Gain"}
            ])
        )
        anns.append(ann_ht)

    if "Images BF" in img_metadata and int(img_metadata["Images BF"]) > 0:
        ann_bf = model.MapAnnotation(
            id="Annotation:2",
            namespace="brightfield",
            description="Additional metadata for brightfield image",
            value=model.Map(ms=[
                    {"value": img_metadata["BF_Camera_Shutter"], "k": "BF_ExposureTime"},
                    {"value": img_metadata["BF_Light_Intensity"], "k": "BF_Intensity"}
            ])
        )
        anns.append(ann_bf)

    ann_fl = []
    if "Images FL" not in img_metadata or int(img_metadata["Images FL3D"]) > 0:
        colors_dict = {0: "blue", 1: "green", 2: "red"}
        for i in range(3):
            if img_metadata["FLCH{}_Enable".format(i)] == "true":
                ann_fl.append(
                    model.MapAnnotation(
                        id="Annotation:{}".format(i+3),
                        namespace="fluorescence",
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
    anns.extend(ann_fl)

    if len(tiling_info) > 0:
        ann_tiling = model.MapAnnotation(
            id="Annotation:6",
            namespace="tiling",
            description="Spatial and temporal tiling information",
            value=model.Map(ms=[
                {"value": tiling_info["tile_img_id"], "k": "Tiling_ClusterID"},
                {"value": tiling_info["tile_total_images"], "k": "Tiling_TotalTilesInImage"},
                {"value": tiling_info["tile_number"], "k": "Tiling_NumberInImage"},
                {"value": tiling_info["tile_row"], "k": "Tiling_Row"},
                {"value": tiling_info["tile_column"], "k": "Tiling_Column"},
                {"value": tiling_info["tile_total_timesteps"], "k": "Tiling_TotalTimesteps"},
                {"value": tiling_info["tile_timestep"], "k": "Tiling_Timestep"},
                {"value": tiling_info["tile_timestep_size"], "k": "Tiling_Timedelta"},
            ])
        )
        anns.append(ann_tiling)

    return anns


def def_plane(x_coord, y_coord, z_coord, delta_t, thec, thet, thez, exposure):
    """Create ome-types Plane with information for each x-y image plane with varying z / time / channel.

    :param x_coord: Center of the plane on the stage in x (in mm)
    :param y_coord: Center of the plane on the stage in y (in mm)
    :param z_coord: z-position of the stage (in mm)
    :param delta_t: Time point of the plane (/recording) in seconds
    :param thec: Number of the channel
    :param thet: Number of the time step
    :param thez: Number of the z plane
    :param exposure: Exposure time in milliseconds

    :return: ome-types Plane
    """
    plane = model.Plane(
        the_c=thec,
        the_t=thet,
        the_z=thez,
        position_x=x_coord,
        position_y=y_coord,
        position_z=z_coord,
        position_x_unit="mm",
        position_y_unit="mm",
        position_z_unit="mm",
        delta_t=delta_t,
        delta_t_unit="s",
        exposure_time=exposure,
        exposure_time_unit="ms"
    )
    return plane


def build_ome_xml(
    data_use,
    offset,
    channels,
    timestamp,
    description,
    experiment,
    experimenter,
    instrument,
    ht_fl_shift,
    data_type,
    ann_ids,
    planes
):
    """Create OME-XML file from given ome-types metadata

    :param data_use: raw tcf/h5 input data with metadata
    :param offset: int: plane offset
    :param channels: list of ome-types Channels used in image
    :param timestamp: str: timestamp in YYYY-MM-DD format the image was acquired at
    :param description: ome-types Description of the image
    :param experiment: ome-types Experiment the image was part of
    :param experimenter: ome-types Experimenter who took the image
    :param instrument: ome-types Instrument the image was taken with
    :param ht_fl_shift: ome-types Stagelabel to report the shift between HT and FL images
    :param data_type: Python data type of the image data
    :param ann_ids: IDs of annotations with additional image metadata
    :param planes: list of ome-types Planes in the image
    :return: ome-types Image with relevant metadata
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
        planes=planes
    )

    image = model.Image(
        pixels=pixels,
        acquisition_date=timestamp,
        name=description,
        description=description,
        experiment_ref=model.ExperimentRef(id=experiment.id),
        experimenter_ref=model.ExperimenterRef(id=experimenter.id),
        instrument_ref=model.InstrumentRef(id=instrument.id),
        annotation_refs=[model.AnnotationRef(id=i) for i in ann_ids],
        stage_label=ht_fl_shift
    )

    return image, offset + n_planes


def read_basic_user_config(filepath):
    """Read user-created file with metadata needed to create the OME-TIFF.

    :param filepath: Path of csv file with metadata
    :return: Dict containing the basic OME metadata
    """

    logging.debug("Reading basic OME config from {}".format(filepath))
    with open(filepath) as f:
        config_dat = f.readlines()
    config_dat = [item.split(",", 1) for item in config_dat if item not in ("\n", "\r\n")]
    config_dict = {item[0]: item[1].strip("\r\n").strip("\n") for item in config_dat}
    return config_dict


def def_ome_basic_md(config_dict):
    """Create experimenter and project metadata dictionaries needed to
    create the OME-TIFF from user-provided metadata.

    :param config_dict: Dict of user-created metadata
    :return: Dict containing metadata needed for OME-TIFF

    """

    basic_ome_md = dict()
    basic_ome_md["exper"] = def_experimenter(
        config_dict["exper_id"],
        config_dict["exper_email"],
        config_dict["exper_inst"],
        config_dict["exper_firstn"],
        config_dict["exper_lastn"],
        config_dict["exper_usern"],
    )
    basic_ome_md["exper_group"] = def_experimenter_group(
        config_dict["eg_id"],
        config_dict["eg_desc"],
        [model.ExperimenterRef(id=config_dict["exper_id"])],
        [model.Leader(id=config_dict["eg_leaders"])],
        config_dict["eg_name"]
    )
    basic_ome_md["proj"] = def_project(
        config_dict["proj_id"], config_dict["proj_name"], config_dict["proj_desc"]
    )
    return basic_ome_md


def create_overall_config(basic_config_path):
    """Create dict with overall metadata that contains both the raw metadata read
from the user-provided file and metadata created from it that is needed
to create the OME-TIFF.

    :param basic_config_path: Path of csv file with basic metadata
    :return: Dict containing the overall metadata that can be used for all folders in one top folder

    """
    basic_config_dict = read_basic_user_config(basic_config_path)
    basic_ome_config_md = def_ome_basic_md(basic_config_dict)
    overall_md = dict(basic_config_dict, **basic_ome_config_md)
    return overall_md


def read_image_config(folder):
    """Read auto-generated files with config data from image folder (config.dat, JobParameter.tcp, position.txt) and
    return dict.

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

    # read and treat position.txt
    with open(join(folder, "position.txt")) as f:
        exp_config_dat_3 = f.readlines()

    exp_config_dat_3 = [float(item.rstrip("\n")) for item in exp_config_dat_3 if item != "\n"]
    exp_config_dict_3 = {
        "x_rec": exp_config_dat_3[0],
        "y_rec": exp_config_dat_3[1],
        "z_rec": exp_config_dat_3[2],
        "c_rec": exp_config_dat_3[3]
    }

    # merge
    exp_config_dict = {item[0]: item[1] for item in exp_config_dat_1}
    exp_config_dict.update({item[0]: item[1] for item in exp_config_dat_2})
    exp_config_dict.update(exp_config_dict_3)

    return exp_config_dict


def read_tiling_info(folder):
    """Read tiling info for image.

    :param folder: Folder name as string
    :return: dict containing the per-image tiling data
    """
    def convert_to_float(item):
        try:
            if "." in item:
                return float(item)
            return int(item)
        except ValueError:
            return item.strip()

    try:
        with open(join(folder, "tiling_info.txt")) as f:
            tiling_info = f.readlines()

        tmp = [item.split(",") for item in tiling_info]
        tiling_dict = {item[0]: convert_to_float(item[1]) for item in tmp}
    except FileNotFoundError:
        logging.debug("Tiling info not found.")
        tiling_dict = {}

    return tiling_dict


def define_image_metadata(overall_config_dict, img_config_dict, tiling_dict):
    """Integrate project and image metadata to obtain comprehensive metadata dict
used to create the OME-TIFF.

    :param overall_config_dict: dict with overall metadata given by the user
    :param img_config_dict: dict with per-image metadata extracted from config file in image folder
    :param tiling_dict: dict with per-image tiling information
    :returns: dict containing all metadata to create the OME-TIFF.

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

    img_metadata["anns"] = def_annotations(img_config_dict, tiling_dict)

    return img_metadata


def transform_tcf(folder, overall_md, output_xml=False, include_mip: bool = True):
    """Parse an image in a folder that has the same name as the folder
    and additionally ends with .TCF. The parsed OME-TIFF image is stored in the
    same folder. It loops over all imaging modalities contained in the TCF H5F
    file and transforms them into suitable numpy arrays. Relevant metadata is
    taken both from the config file passed by the user as well as from the .TCF
    file.

    :param folder: Relative or absolute file path to folder containing image
    :param overall_md: Overall metadata dict
    :param output_xml: If True, output the ome-xml file alongside the ome-tiff file
    :param include_mip: If True, maximum intensity projections are included in the
    output ome tiff file

    """

    folder = folder.rstrip("/")
    try:
        exp_config_dict = read_image_config(folder)
    except Exception as e:
        raise Exception("Skipping folder {} with Exception {}".format(folder, e))

    tiling_dict = read_tiling_info(folder)

    ome_img_md = define_image_metadata(overall_md, exp_config_dict, tiling_dict)
    # timestamp = get_img_timestamp(folder)

    # open HDF5 image (TCF)
    logging.debug("Reading image")
    dat = h5py.File(join(folder, basename(folder) + ".TCF"), "r")
    # file_name_store = join(top_folder, folder, folder + ".ome.tiff")
    file_name_store = join(folder, basename(folder) + ".ome.tiff")
    img_ome_xmls = []
    imgs = []
    plane_offset = 0  # for multiple timesteps / channels

    keys_to_loop = list(dat["Data"].keys())
    if not include_mip:
        keys_to_loop = [item for item in keys_to_loop if not "MIP" in item]
    # FL channels are nested one level below imaging modalities --> (ugly) trick to achieve them in a similar way
    if "2DFLMIP" in keys_to_loop:
        n_chans = len(dat["Data"]["2DFLMIP"])
        keys_to_loop.extend((n_chans-1)*["2DFLMIP"])
        fl_mip_counter = 0
    if "3DFL" in keys_to_loop:
        n_chans = len(dat["Data"]["3DFL"])
        keys_to_loop.extend((n_chans-1)*["3DFL"])
        fl_3d_counter = 0

    for i_chan, name in enumerate(keys_to_loop):
        logging.debug("Working on {}".format(name))
        data_use = dat["Data"][name]
        # stagelabel = def_ht_fl_shift_stagelabel(exp_config_dict["x_rec"], exp_config_dict["y_rec"], 0, 0, 0)
        stagelabel = None

        if name == "2DMIP":
            channels = [ome_img_md["channel_ht"].model_copy()]  # workaround for channel IDs
            description = "2D Holotomography Maximum Intensity Projection"
            data_type = "uint16"
            img_formatted = np.array(
                [data_use[item][()][np.newaxis] for item in data_use]
            )[np.newaxis]
            ann_ref = 1
            timestamp = data_use["000000"].attrs["RecordingTime"][0].decode("utf-8")
            exposure = exp_config_dict["Camera Shutter"]

        elif name == "2D":
            channels = [ome_img_md["channel_ht"].model_copy()]  # workaround for channel IDs
            description = "2D Phasemap"
            data_type = "float"
            img_formatted = np.array([data_use[item][()] for item in data_use])[
                np.newaxis
            ]
            ann_ref = 1
            timestamp = data_use["000000"].attrs["RecordingTime"][0].decode("utf-8")
            exposure = exp_config_dict["Camera Shutter"]

        elif name == "BF":
            channels = [ome_img_md["channel_bf"].model_copy()]  # workaround for channel IDs
            description = "2D Brightfield"
            data_type = "uint8"
            img_formatted = np.array([data_use[item][0] for item in data_use])[
                np.newaxis
            ]
            ann_ref = 2
            timestamp = data_use["000000"].attrs["RecordingTime"][0].decode("utf-8")
            exposure = exp_config_dict["BF_Camera_Shutter"]

        elif name == "3D":
            channels = [ome_img_md["channel_ht"].model_copy()]  # workaround for channel IDs
            description = "3D Holotomography"
            data_type = "uint16"
            img_formatted = np.array([data_use[item][()] for item in data_use])[
                np.newaxis
            ]
            ann_ref = 1
            timestamp = data_use["000000"].attrs["RecordingTime"][0].decode("utf-8")
            exposure = exp_config_dict["Camera Shutter"]

        elif name == "2DFLMIP":
            channel = list(data_use.keys())[fl_mip_counter]

            channels = [ome_img_md["channel_fl{}".format(channel[2])].model_copy()]  # workaround for channel IDs]
            description = "2D {} Maximum Intensity Projection"\
                .format(ome_img_md["channel_fl{}".format(channel[2])].name)
            data_type = "uint16"
            img_formatted = np.array(
                [data_use[channel][item][()][np.newaxis] for item in data_use[channel]]
            )[np.newaxis]
            ann_ref = 3 + int(channel[2])
            timestamp = data_use[channel]["000000"].attrs["RecordingTime"][0].decode("utf-8")
            exposure = exp_config_dict["FLCH{}_Camera_Shutter".format(channel[2])]

            fl_mip_counter += 1

        elif name == "3DFL":
            channel = list(data_use.keys())[fl_3d_counter]

            channels = [ome_img_md["channel_fl{}".format(channel[2])].model_copy()]  # workaround for channel IDs
            description = "3D {}".format(ome_img_md["channel_fl{}".format(channel[2])].name)
            data_type = "uint16"
            img_formatted = np.array([data_use[channel][item][()] for item in data_use[channel]])[
                np.newaxis
            ]
            ann_ref = 3 + int(channel[2])
            timestamp = data_use[channel]["000000"].attrs["RecordingTime"][0].decode("utf-8")
            stagelabel = def_ht_fl_shift_stagelabel(
                dat["Data"]["3DFL"].attrs["OffsetZ"],
                # dat["Data"]["3D"].attrs["ResolutionZ"] * dat["Data"]["3D"].attrs["SizeZ"],
                dat["Data"]["3DFL"].attrs["ResolutionZ"] * dat["Data"]["3DFL"].attrs["SizeZ"]
            )
            exposure = exp_config_dict["FLCH{}_Camera_Shutter".format(channel[2])]

            fl_3d_counter += 1

        else:
            logging.info("Skipping unknown data type {}".format(name))
            continue

        channels[0].id = "Channel:{}".format(i_chan)

        try:
            planes = [def_plane(
                    exp_config_dict["x_rec"],
                    exp_config_dict["y_rec"],
                    exp_config_dict["z_rec"],
                    tiling_dict["tile_timestep"]*tiling_dict["tile_timestep_size"],
                    i_chan,
                    tiling_dict["tile_timestep"],
                    k_plane,
                    exposure
                ) for k_plane in range(img_formatted.shape[2])]
            ann_refs = [0, ann_ref, 6]
        except KeyError:
            # try:
                planes = [def_plane(
                    exp_config_dict["x_rec"],
                    exp_config_dict["y_rec"],
                    exp_config_dict["z_rec"],
                    j_time*data_use.attrs["TimeInterval"][0],
                    i_chan,
                    j_time,
                    k_plane,
                    exposure
                ) for j_time, k_plane in np.ndindex(img_formatted.shape[1:3])]
                ann_refs = [0, ann_ref]
            # except KeyError:
            #     print("here")
            #     planes = []
            #     ann_refs = [0, ann_ref]
        # logging.warning("TIMESTAMP: {}".format(timestamp))

        tzinfo = datetime.now().astimezone().tzinfo
        dt = datetime.strptime(timestamp[:-4], '%Y-%m-%d %H:%M:%S').replace(tzinfo=tzinfo)
        # logging.warning("dt = {}".format(dt))

        try:
            xml, plane_offset = build_ome_xml(
                data_use,
                plane_offset,
                channels,
                dt,
                description,
                ome_img_md["exp"],
                overall_md["exper"],
                ome_img_md["instr"],
                stagelabel,
                data_type,
                ["Annotation:{}".format(item) for item in ann_refs],
                planes
            )
        except Exception as e:
            raise Exception("Exception during xml building: {}".format(e))

        img_ome_xmls.append(xml)
        imgs.append(img_formatted)

    ome_xmls = model.OME(
        creator="tcf_to_ometiff by Henning Zwirnmann v{}".format(__version__),
        images=img_ome_xmls,
        experiments=[ome_img_md["exp"]],
        experimenters=[overall_md["exper"]],
        experimenter_groups=[overall_md["exper_group"]],
        instruments=[ome_img_md["instr"]],
        structured_annotations=ome_img_md["anns"]
    )

    logging.debug("Writing file {}".format(file_name_store))
    OmeTiffWriter.save(
        imgs,
        file_name_store,
        ome_xml=ome_xmls,
        tifffile_kwargs={"compression": "zlib", "compressionargs": {"level": 9}},
    )

    if output_xml:
        xml_out = ome_xmls.to_xml()
        with open(join(folder, basename(folder) + ".ome.xml"), "w") as fn:
            fn.write(xml_out)


def transform_folder(top_folder, basic_config_path, output_xml=False,
                     include_mip: bool = True):
    """Parse images stored in subfolders of a top folder. This is the
    standard TomoStudio case when on each date a new top folder is created that
    has one subfolder for each snapshot. The parsed OME-TIFF images are stored
    in the respective subfolders.

    :param top_folder: Relative or absolute file path to folder containing
    image
    :param basic_config_path: Relative or absolute file path to csv file with
    basic metadata
    :param output_xml: If True, output the ome-xml files alongside the ome-tiff
    files
    :param include_mip: If True, maximum intensity projections are included in
    the output ome tiff files

    """
    overall_md = create_overall_config(basic_config_path)

    logging.info("Traversing folders in {}".format(top_folder))
    folders = [d for d in listdir(top_folder) if isdir(join(top_folder, d))]
    for folder in folders:
        print(folder)
        logging.info("Reading folder {}".format(folder))
        try:
            transform_tcf(join(top_folder, folder), overall_md, output_xml, include_mip)
        except Exception as e:
            print(e)
            logging.info(e)
            continue
