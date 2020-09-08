"""Methods to approximate bluespot water levels and extents in the final state"""
import logging
import numpy as np
from malstroem.algorithms.label import set_label_to_value
from malstroem.hyps import Histogram, HistogramBinsInfo, hypsometrystats_from_flatdict

logger = logging.getLogger(__name__)

def _cumulative_volume(h : Histogram, cell_area : float):
    """Calculates the bluespot volume below each bin in the z histogram"""
    # Volume of previous step is the cumulative number of cells below this step
    cumulative = np.cumsum(h.counts, dtype=np.float64)
    # Shift by one
    cumulative_below = np.concatenate(([0.0], cumulative[:-1]))
    prev_step_volumes = cell_area * h.bins.resolution * cumulative_below
    # Cumulative volumes per bin
    cumul_volumes = np.cumsum(prev_step_volumes)
    return cumul_volumes
    

def _bin_waterlevel_z(bin_info : HistogramBinsInfo):
    """Calculates bin centre Z values"""
    return np.arange(0,bin_info.num_bins) * bin_info.resolution + bin_info.lower_bound + bin_info.resolution * 0.5

def approx_water_level_io(finalvols_reader, hyps_reader, levels_writer):
    """Calculate approximate water level Z in each bluespot for a given final state.

    Uses histogram info for each bluespot to map between the final state water volume and an estimated
    water level Z. 
    """
    def parse_hyps_feature(hyps_feature):
        props = hyps_feature["properties"]
        bsid = int(props["bspot_id"])
        hyps = hypsometrystats_from_flatdict(props)
        cell_area = float(props["cell_area"])
        max_depth = float(props["bspot_dmax"])
        max_vol = float(props["bspot_vol"])
        return {"bspot_id":bsid, "hyps":hyps, "cell_area": cell_area, "max_depth": max_depth, "max_vol": max_vol}

    hyps_index = {int(gjn['properties']['bspot_id']): gjn for gjn in hyps_reader.read_geojson_features()}
    bspot_finalstate_features = [x for x in finalvols_reader.read_geojson_features() if x["properties"]["nodetype"] == "pourpoint"]
    for bspot_finalstate in bspot_finalstate_features:
        props = bspot_finalstate["properties"]
        bsid = int(props["bspot_id"])
        final_vol = float(props["v"])

        h = parse_hyps_feature(hyps_index[bsid])

        zmin = h["hyps"].zmin
        zmax = h["hyps"].zmax
        max_vol = h["max_vol"]
        water_level = None
        if max_vol == 0 or final_vol / max_vol > 0.9999:
            # waterlevel is the maximum possible in this bluespot
            water_level = h["hyps"].zmin + h["max_depth"]
        else:
            # Calculate estimate
            # Cumulative volume for each histogram bin
            cum_vol = _cumulative_volume(h["hyps"].zhistogram, h["cell_area"])
            # Z value of centre of each histogram bin
            binsz = _bin_waterlevel_z(h["hyps"].zhistogram.bins)
            # Replace bounds with acutal values. Zero volume at zmin and max_volume at zmax
            volumes = np.concatenate(([0.0], cum_vol[1:-1], [max_vol]))
            z = np.concatenate(([zmin], binsz[1:-1], [zmax])) 
            # Now interpolate for final_vol
            water_level = np.interp([final_vol], volumes, z)[0]
        assert water_level is not None, "Water level calculation failed"
        props["approx_z"] = float(water_level)
        props["approx_dmax"] = float(water_level) - zmin

    levels_writer.write_geojson_features(bspot_finalstate_features)

def approx_bluespots_io(
        bluespot_labels_reader, 
        bluespot_water_levels_reader, 
        dem_reader, 
        approx_depths_writer = None, 
        approx_bluespot_labels_writer = None,  
        background_label=0):

    if not approx_depths_writer and not approx_bluespot_labels_writer:
        raise Exception("At least one output writer must be specified")

    logger.info("Reading approximated water levels")
    # Make bluespot_id -> bluespot_waterlevel_z dictionary
    bluespot_water_levels = { int(x["properties"]["bspot_id"]) : float(x["properties"]["approx_z"]) for x in bluespot_water_levels_reader.read_geojson_features() if x["properties"]["nodetype"] == "pourpoint"}
    # turn into list (list index == bluespot_id)
    value_list = _labelvaluedict_to_list(bluespot_water_levels, background=background_label)

    logger.info("Reading bluespot labels")
    bluespot_labels = bluespot_labels_reader.read()

    logger.info("Set water levels")
    # Make raster with bluespot labels replaced by their water level Z 
    # This raster may have cells where water level z is below terrain z
    maxextent_waterlevel = set_label_to_value(bluespot_labels, value_list)
    # Conserve memory
    del bluespot_labels

    logger.info("Read DEM")
    dem = dem_reader.read()

    logger.info("Calculate depths")
    # subtract dem to get depths (we get negative depths where bluespot water level is below ground)
    depths = maxextent_waterlevel - dem
    del dem

    # Use mask for areas with negative depths and set the depth in these areas to 0
    below = depths < 0
    depths[below] = 0

    if approx_depths_writer:
        logger.info("Write approximate depths")
        approx_depths_writer.write(depths)

    del depths
    if approx_bluespot_labels_writer:
        logger.info("Writing bluespot labels for approximate extents")
        bluespot_labels = bluespot_labels_reader.read()
        bluespot_labels[below] = background_label
        approx_bluespot_labels_writer.write(bluespot_labels)


def approx_bluespots(bluespot_labels, bluespot_water_levels, dem, background_label=0 ):
    """Approximate extents and depths of bluespots given a water level z per bluespot.

    NOTE: This method alters the input bluespot_labels array. This is to conserve memory.

    Parameters
    ----------
    bluespot_labels : ndarray
        An integer ndarray where each value indicates a unique bluespot calculated in the maximum filled scenario.
    bluespot_water_levels : dict
        A dictionary which maps bluespot label (int) to a bluespot water level Z (float)
    dem : ndarray
        A float ndarray of DEM data
    background_label : int, optional
        Label of 'background' (ie non-bluespot cells), by default 0

    Returns
    -------
    tuple (bluespot_labels, depths)
        First element is a reference to the input bluespot_labels ndarray which is updated to show only approximated extent of
        bluespots. Second element is a float ndarray with approximated depths.
    """
    value_list = _labelvaluedict_to_list(bluespot_water_levels, background=background_label)

    # Make raster with bluespot labels replaced by their water level Z 
    # This raster may have cells where water level z is below terrain z
    maxextent_waterlevel = set_label_to_value(bluespot_labels, value_list)

    # subtract dem to get depths (we get negative depths where bluespot water level is below ground)
    depths = maxextent_waterlevel - dem

    # Use mask for areas with negative depths and set the depth in these areas to 0
    below = depths < 0
    depths[below] = 0

    # Use mask to return labels of approximate bluespots
    bluespot_labels[below] = background_label
    return bluespot_labels, depths





def _labelvaluedict_to_list(labelvaluedict, background=0, set_background_to=-999.0):
    max_label = max([x for x in labelvaluedict.keys()])
    l = []
    for ix in range(max_label + 1):
        # This ensures that we have a value per ix (except for the background label)
        if ix == background:
            l.append(set_background_to)
        else:
            l.append(labelvaluedict[ix])
    return l


def _estimate_waterlevel(bs_vol_info, at_vol, bs_max_z = None):
    """Interpolates a Z value for a given fill volume [m3]"""
    cum_volumes = bs_vol_info[1]
    z = bs_vol_info[2]
    # TODO: add values maximum volume and maximum waterlevel Z at the end
    # ALso add 0m3 and zmin at the start.
    return np.interp([at_vol], cum_volumes, z, right = bs_max_z)[0]