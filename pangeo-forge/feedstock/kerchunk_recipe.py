import aiohttp
import apache_beam as beam
from netrc import netrc
from pangeo_forge_recipes.transforms import OpenWithKerchunk, CombineReferences, WriteCombinedReference
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
    | OpenWithKerchunk(
        storage_options = {"client_kwargs": client_kwargs},
    )
    | CombineReferences(
        concat_dims = pattern.concat_dims,
        identical_dims = ["lat", "lon"],
    )
    | WriteCombinedReference(
        store_name = 'gpm-kerchunk',
    )
)
