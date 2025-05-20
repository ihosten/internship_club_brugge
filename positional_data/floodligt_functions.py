import numpy as np
from pathlib import Path
import json
from floodlight.io.secondspectrum import read_teamsheets_from_meta_json
import json
from typing import Union, Tuple, Dict
from pathlib import Path
from floodlight.core.pitch import Pitch
from floodlight.io.utils import get_and_convert
from floodlight.core.teamsheet import Teamsheet
from floodlight.core.xy import XY
from floodlight.core.code import Code

            
def clean_metadata(filepath_metadata: Union[str, Path]):
    "function to modify the metadata data frame in order to match the floodlight functions input"
    with open(str(filepath_metadata), "r") as f:
        raw_meta = json.load(f)
        
        meta_flat = raw_meta["data"]
        
        meta_flat["fps"] = 25
        
        for period in meta_flat.get("periods", []):
            period["startFrameIdx"] = period.pop("startFrameClock", None)
            period["endFrameIdx"] = period.pop("endFrameClock", None)
            
            if not period.get("number"):
                period["number"] = 1
        
        meta_flat["homePlayers"] = meta_flat["homeTeam"]["players"]
        meta_flat["awayPlayers"] = meta_flat["awayTeam"]["players"]
        
        with open("cleaned_metadata.json", "w") as f:
            json.dump(meta_flat, f)
            
            
def _read_metajson(filepath_metadata: Union[str, Path]) -> Tuple[Dict, Dict, Dict, Pitch]:
    """Reads Second Spectrums's metadata file and extracts information about match
    metainfo, periods, playing directions, and the pitch.

    Parameters
    ----------
    filepath_metadata: str or pathlib.Path
        Full path to _meta.json file.

    Returns
    -------
    metadata: dict
        Dictionary with meta information such as framerate.
    periods: Dict[Tuple[int, int]]
        Dictionary with start and endframes of all segments, e.g.,
        ``periods[segment] = (startframe, endframe)``.
    directions: Dict[str, Dict[str, str]]
        Dictionary with playing direction information of all segments and teams,
        e.g., ``directions[segment][team] = 'lr'``
    pitch: Pitch
        Pitch object with actual pitch length and width.
    """
    # read file
    with open(str(filepath_metadata), "r") as f:
        metajson = json.load(f)

    # bin
    metadata = {}
    periods = {}
    directions = {}

    # assemble metadata
    metadata["framerate"] = metajson.get("fps", None)
    metadata["length"] = metajson.get("pitchLength", None)
    metadata["width"] = metajson.get("pitchWidth", None)
    metadata["home_tID"] = get_and_convert(metajson, "homeOptaId", int)
    metadata["away_tID"] = get_and_convert(metajson, "awayOptaId", int)

    # get period information
    for period in metajson["periods"]:
        segment = f"HT{period['number']}"
        periods[segment] = (period["startFrameIdx"], period["endFrameIdx"] + 1)

    # get playing direction
    for period in metajson["periods"]:
        segment = f"HT{period['number']}"
        directions[segment] = {}
        if period["homeAttPositive"]:
            directions[segment]["Home"] = "lr"
            directions[segment]["Away"] = "rl"
        else:
            directions[segment]["Home"] = "rl"
            directions[segment]["Away"] = "lr"

    # generate pitch object
    pitch = Pitch.from_template(
        template_name="secondspectrum",
        length=metadata["length"],
        width=metadata["width"],
        sport="football",
    )

    return metadata, periods, directions, pitch

#slightly adapted function using wallclock instead of framerate
def read_position_data_jsonl(
    filepath_position: Union[str, Path],
    filepath_metadata: Union[str, Path],
    teamsheet_home: Teamsheet = None,
    teamsheet_away: Teamsheet = None,
) -> Tuple[
    Dict[str, Dict[str, XY]],
    Dict[str, Code],
    Dict[str, Code],
    Dict[str, Teamsheet],
    Pitch,
]:
    """Parse Second Spectrum files and extract position data, possession and ballstatus
    codes, as well as pitch information.

    Second Spectrum data is typically stored in two separate files, a .jsonl file
    containing the actual data as well as a _meta.json containing information about
    pitch size, framerate, lineups and start- and endframes of match periods. This
    function provides a high-level access to Second Spectrum data by parsing "the full
    match" given both files.

    Parameters
    ----------
    filepath_position: str or pathlib.Path
        Full path to .jsonl-file.
    filepath_metadata: str or pathlib.Path
        Full path to _meta.json file.
    teamsheet_home: Teamsheet, optional
        Teamsheet object for the home team used to create link dictionaries of the form
        `links[team][jID] = xID`. The links are used to map players to a specific xID
        in the respective XY objects. Should be supplied for custom ordering. If given
        as None (default), teamsheet is extracted from the meta.json file and xIDs are
        assigned based on the ordering determined by the
        ``read_teamsheets_from_metajson`` function (see for details).
    teamsheet_away: Teamsheet, optional
        Teamsheet object for the away team. If given as None (default), teamsheet is
        extracted from the meta.json-file. See teamsheet_home for details.

    Returns
    -------
    data_objects: Tuple[Dict[str, Dict[str, XY]], Dict[str, Code], Dict[str, Code], \
     Dict[str, Teamsheet], Pitch]
        Tuple of (nested) floodlight core objects with shape (xy_objects,
        possession_objects, ballstatus_objects, teamsheets, pitch).

        ``xy_objects`` is a nested dictionary containing ``XY`` objects for each team
        and segment of the form ``xy_objects[segment][team] = XY``. For a typical
        league match with two halves and teams this dictionary looks like:
        ``{'HT1': {'Home': XY, 'Away': XY}, 'HT2': {'Home': XY, 'Away': XY}}``.

        ``possession_objects`` is a dictionary containing ``Code`` objects with
        possession information (home or away) for each segment of the form
        ``possession_objects[segment] = Code``.

        ``ballstatus_objects`` is a dictionary containing ``Code`` objects with
        ballstatus information (dead or alive) for each segment of the form
        ``ballstatus_objects[segment] = Code``.

        ``teamsheets`` is a dictionary containing ``Teamsheet`` objects for each team
        of the form ``teamsheets[team] = Teamsheet``.

        ``pitch`` is a ``Pitch`` object corresponding to the data.
    """
    # setup
    metadata, periods, directions, pitch = _read_metajson(str(filepath_metadata))
    segments = list(periods.keys())
    teams = ["Home", "Away"]
    fps = int(metadata["framerate"])
    status_link = {True: "A", False: "D"}
    key_map = {"Home": "homePlayers", "Away": "awayPlayers"}

    # create or check teamsheet objects
    if teamsheet_home is None and teamsheet_away is None:
        teamsheets = read_teamsheets_from_meta_json(filepath_metadata)
        teamsheet_home = teamsheets["Home"]
        teamsheet_away = teamsheets["Away"]
    elif teamsheet_home is None:
        teamsheets = read_teamsheets_from_meta_json(filepath_metadata)
        teamsheet_home = teamsheets["Home"]
    elif teamsheet_away is None:
        teamsheets = read_teamsheets_from_meta_json(filepath_metadata)
        teamsheet_away = teamsheets["Away"]
    else:
        pass
        # potential check

    # create links
    if "xID" not in teamsheet_home.teamsheet.columns:
        teamsheet_home.add_xIDs()
    if "xID" not in teamsheet_away.teamsheet.columns:
        teamsheet_away.add_xIDs()
    links_jID_to_xID = {
        "Home": teamsheet_home.get_links("jID", "xID"),
        "Away": teamsheet_away.get_links("jID", "xID"),
    }

    # bins
    xydata = {
        team: {
            segment: np.full(
                [
                    periods[segment][1] - periods[segment][0],  # T frames in segment
                    len(links_jID_to_xID[team]) * 2,  # N players in team
                ],
                np.nan,
            )
            for segment in segments
        }
        for team in teams
    }
    xydata["Ball"] = {
        segment: np.full([periods[segment][1] - periods[segment][0], 2], np.nan)
        for segment in segments
    }
    codes = {
        code: {
            segment: np.full(
                [periods[segment][1] - periods[segment][0]], np.nan, dtype=object
            )
            for segment in segments
        }
        for code in ["possession", "ballstatus"]
    }

    # loop
    with open(str(filepath_position), "r") as f:
        while True:
            # get one line of file
            dataline = f.readline()
            # terminate if at end of file
            if len(dataline) == 0:
                break
            # load json
            dataline = json.loads(dataline)

            # get dataline meta information and correct for frame offset
            segment = f"HT{dataline['period']}"
            frame_abs = dataline["wallClock"]
            frame_rel = (frame_abs - periods[segment][0]) // 40 # samling rate = 25 Hz = 40ms --> devide by this to find the correct frame

            # insert (x,y)-data into correct np.array, at correct place (t, xID)
            for team in teams:
                player_data = dataline[key_map[team]]
                for player in player_data:
                    # map jersey number to array index and infer respective columns
                    jID = player["number"]
                    x_col = (links_jID_to_xID[team][jID]) * 2
                    y_col = (links_jID_to_xID[team][jID]) * 2 + 1
                    xydata[team][segment][frame_rel, (x_col, y_col)] = player["xyz"][:2]

            # get ball data
            if "ball" in dataline and dataline["ball"].get("xyz") is not None:
                xydata["Ball"][segment][frame_rel] = dataline["ball"]["xyz"][:2]

            # get codes
            if "lastTouch" in dataline:
                possession = dataline["lastTouch"][0].upper()
            else:
                possession = None
            codes["possession"][segment][frame_rel] = possession
            if "live" in dataline:
                ballstatus = status_link[dataline["live"]]
            else:
                ballstatus = None
            codes["ballstatus"][segment][frame_rel] = ballstatus

    # create objects
    xy_objects = {}
    possession_objects = {}
    ballstatus_objects = {}
    for segment in segments:
        xy_objects[segment] = {}
        possession_objects[segment] = Code(
            code=codes["possession"][segment],
            name="possession",
            definitions={"H": "Home", "A": "Away"},
            framerate=fps,
        )
        ballstatus_objects[segment] = Code(
            code=codes["ballstatus"][segment],
            name="ballstatus",
            definitions={"D": "Dead", "A": "Alive"},
            framerate=fps,
        )
        for team in ["Home", "Away"]:
            xy_objects[segment][team] = XY(
                xy=xydata[team][segment],
                framerate=fps,
                direction=directions[segment][team],
            )
        xy_objects[segment]["Ball"] = XY(xy=xydata["Ball"][segment], framerate=fps)
    teamsheets = {
        "Home": teamsheet_home,
        "Away": teamsheet_away,
    }

    # pack objects
    data_objects = (
        xy_objects,
        possession_objects,
        ballstatus_objects,
        teamsheets,
        pitch,
    )

    return data_objects