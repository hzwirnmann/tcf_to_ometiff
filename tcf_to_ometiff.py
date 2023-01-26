from os.path import join
import sys

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
    return model.Microscope(
        id=mic_id,
        manufacturer="Tomocube Inc.",
        model="HT-2H",
        serial_number=sn,
        lot_number=lot,
        type="Other",
    )


def def_det(det_id):
    return model.Detector(id=det_id, type="CCD")


def def_obj(obj_id, lens_na, lens_magn, immersion):
    return model.Objective(id=obj_id,
                           lens_na=lens_na,
                           nominal_magnification=lens_magn,
                           immersion="Water")


def def_light_source(light_source_id):
    return model.Laser(
        id=light_source_id,
        power=0.05,
        tuneable=False,
        type="SolidState",
        wavelength=532,
    )


def def_instr(instr_id, microscope, detectors, light_sources):
    return model.Instrument(
        id=instr_id,
        microscope=microscope,
        detectors=detectors,
        light_source_group=light_sources,
    )


def def_channel(chan_id, ls_id):
    return model.Channel(
        id=chan_id,
        acquisition_mode="Other",
        contrast_method="Phase",
        illumination_type="Other",
        name="Holotomography",
        light_source_settings=model.LightSourceSettings(id=ls_id),
        samples_per_pixel=1,
    )


def def_experimenter(exper_id, email, inst, first_name, last_name, user_name):
    return model.Experimenter(
        id=exper_id,
        email=email,
        institution=inst,
        first_name=first_name,
        last_name=last_name,
        user_name=user_name,
    )


def def_experiment(desc, exper):
    return model.Experiment(description=desc, experimenter=exper)


def def_project(proj_id, proj_name, desc):
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
):
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
        type="uint16",
        physical_size_x=round(data_use.attrs["ResolutionX"][0], 2),
        physical_size_y=round(data_use.attrs["ResolutionY"][0], 2),
        physical_size_z=physical_size_z,
        # planes=ht_3d_planes,
        # significant_bits=14,
        tiff_data_blocks=tiffdata,
        time_increment=data_use.attrs["TimeInterval"][0],
        channels=channels,
    )

    image = model.Image(
        # id='Image:2',
        pixels=pixels,
        acquisition_date=timestamp,
        name=description,
        description=description,
        experiment_ref=experiment,
        experimenter_ref=experimenter,
        instrument_ref=instrument,
    )

    return image, offset + n_planes


if __name__ == "__main__":
    logging.info("Reading overall config from {}".format(sys.argv[2]))
    with open(sys.argv[2]) as f:
        config_dat = f.readlines()
    config_dict = {item[0]: item[1] for item in config_dat.split(",", 1)}
    exper = def_experimenter(
        config_dict["exper_id"],
        config_dict["exper_email"],
        config_dict["exper_inst"],
        config_dict["exper_firstn"],
        config_dict["exper_lastn"],
        config_dict["exper_usern"],
    )
    exp = def_experiment(config_dict["exp_desc"], config_dict["exper_id"])
    proj = def_project(config_dict["proj_id"], config_dict["proj_name"],
                       config_dict["proj_desc"])

    top_folder = sys.argv[1]
    logging.info("Traversing folders in {}".format(top_folder))
    for folder in top_folder:
        logging.info("Reading folder {}".format(folder))
        with open(join(top_folder, folder, "config.dat")) as f:
            exp_config_dat = f.readlines()
        exp_config_dict = {
            item[0]: item[1]
            for item in exp_config_dat.split(",", 1)
        }

        mic = def_mic(config_dict["mic_id"], exp_config_dict["Serial"],
                      config_dict["lot"])
        det = def_det(config_dict["det_id"])
        obj = def_obj(
            config_dict["obj_id"],
            exp_config_dict["NA"],
            exp_config_dict["M"],
            exp_config_dict["NA"],
        )
        light_source = def_light_source(config_dict["light_source_id"])
        instr = def_instr(config_dict["instr_id"], mic, [det], [light_source])
        channel_ht = def_channel(config_dict["channel_id"],
                                 config_dict["light_source_id"])

        with open(join(top_folder, folder, "timestamp.txt")) as f:
            timestamp_long = f.read()
            timestamp = (timestamp_long[:4] + "-" + timestamp_long[4:6] + "-" +
                         timestamp_long[6:8] + "T" + timestamp_long[9:11] +
                         ":" + timestamp_long[11:13] + ":" +
                         timestamp_long[13:15])

        dat = h5py.File(join(top_folder, folder, folder + ".TCF"), "r")
        file_name_store = join(top_folder, folder, folder + ".ome.tiff")

        img_ome_xmls = []
        imgs = []
        plane_offset = 0  # for multiple timesteps / channels
        for name in dat["Data"].keys():
            data_use = dat["Data"][name]
            if name == "2DMIP":
                channels = [channel_ht]
                description = "2D Holotomography Maximum Intensity Projection"
                img_formatted = np.array([
                    data_use[item][()][np.newaxis] for item in data_use
                ])[np.newaxis]
            elif name == "3D":
                channels = [channel_ht]
                description = "3D Holotomography"
                img_formatted = np.array(
                    [data_use[item][()] for item in data_use])[np.newaxis]
            else:
                print("No valid data type in {}: {}".format(folder, name))
                sys.exit(-1)

            logging.info("Building xml")
            xml, plane_offset = build_ome_xml(
                data_use,
                plane_offset,
                channels,
                timestamp,
                description,
                exp,
                exper,
                instr,
            )

            img_ome_xmls.append(xml)
            imgs.append(img_formatted)

        ome_xmls = model.OME(
            creator="TCFtoOME by Henning Zwirnmann v0.1",
            images=img_ome_xmls,
            experiments=[exp],
            experimenters=[exper],
            instruments=[instr],
        )

        logging.info("Writing file {}".format(file_name_store))
        writers.ome_tiff_writer.OmeTiffWriter().save(
            imgs,
            file_name_store,
            ome_xml=ome_xmls,
        )
