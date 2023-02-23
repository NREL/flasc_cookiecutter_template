import os
import pandas as pd

from floris.tools import WindRose


def load_windrose(plot=False):
    root_path = os.path.dirname(os.path.abspath(__file__))
    source_path = os.path.join(root_path, "..", "..", "common_windfarm_information")
    df = pd.read_csv(os.path.join(source_path, "windrose.csv"))

    # Create a FLORIS WindRose object based on the user specified data
    wr = WindRose()
    wr.make_wind_rose_from_user_dist(
        wd_raw=df["wd"],
        ws_raw=df["ws"],
        freq_val=df["freq_val"],
        wd=df["wd"].unique(),
        ws=df["ws"].unique(),
    )
    wr.internal_resample_wind_direction()

    if plot:
        wr.plot_wind_rose()
    
    return wr
