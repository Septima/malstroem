"""Methods to approximate bluespot water levels and extents in the final state"""
import numpy as np
from malstroem.hyps import Histogram, HistogramBinsInfo, hypsometrystats_from_flatdict


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
        # Is it completely filled?
        water_level = None
        if final_vol / h["max_vol"] > 0.9999:
            # waterlevel is the maximum passoible in this bluespot
            water_level = h["hyps"].zmin + h["max_depth"]
        else:
            # Calculate estimate
            # Cumulative volume for each histogram bin
            cum_vol = _cumulative_volume(h["hyps"].zhistogram, h["cell_area"])
            # Z value of centre of each histogram bin
            binsz = _bin_waterlevel_z(h["hyps"].zhistogram.bins)
            # Replace bounds with acutal values. Zero volume at zmin and max_volume at zmax
            volumes = np.concatenate(([0.0], cum_vol[1:-1], [h["max_vol"]]))
            z = np.concatenate(([zmin], binsz[1:-1], [zmax])) 
            # Now interpolate for final_vol
            water_level = np.interp([final_vol], volumes, z)[0]
        assert water_level is not None, "Water level calculation failed"
        props["approx_z"] = float(water_level)
        props["approx_dmax"] = float(water_level) - zmin

    levels_writer.write_geojson_features(bspot_finalstate_features)

def _estimate_waterlevel(bs_vol_info, at_vol, bs_max_z = None):
    """Interpolates a Z value for a given fill volume [m3]"""
    cum_volumes = bs_vol_info[1]
    z = bs_vol_info[2]
    # TODO: add values maximum volume and maximum waterlevel Z at the end
    # ALso add 0m3 and zmin at the start.
    return np.interp([at_vol], cum_volumes, z, right = bs_max_z)[0]