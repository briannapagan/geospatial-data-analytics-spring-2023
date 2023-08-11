import aiohttp
import apache_beam as beam
from netrc import netrc
from pangeo_forge_recipes.transforms import OpenURLWithFSSpec, OpenWithXarray, StoreToZarr
from pangeo_forge_cmr import files_from_cmr


# Get the GPM IMERG Late Precipitation Daily data
shortname = 'GPM_3IMERGDL'

pattern = files_from_cmr( # Provide a list of files by querying CMR
    shortname,
    version='06',
    nitems_per_file=1,
    concat_dim='time',  # Describe how the dataset is chunked
)

(username, account,password) = netrc().authenticators("urs.earthdata.nasa.gov")
client_kwargs = {
    "auth": aiohttp.BasicAuth(username, password),
    "trust_env": True,
}

transforms = (
    beam.Create(pattern.items())
    | OpenURLWithFSSpec(
        open_kwargs = {"client_kwargs": client_kwargs},
    )
    | OpenWithXarray(file_type=pattern.file_type)
    | StoreToZarr(
        store_name = 'gpm.zarr', # wherever it goes this is what the name of the file will be
        combine_dims = pattern.combine_dim_keys,
    )
)