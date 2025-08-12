#Data Space Retriever

A Python Class to simplify the simultaneous download of Sentinel products.

## Installation
```
pip install dataspace-downloader
```

## Pre-requisites
An installation of `rclone` and access to ESA's Dataspace S3 service are required to download files.

## How-to
Data is searched and downloaded through a `Downloader()` instance. This object is fed a search configuration (in YAML form) to find Sentinel products matching the request.

0. Import the library:
```
import dataspace_downloader as dd
```

1. Create a Fetcher instance:

```
D = dd.Downloader("my_parameters.yml")
```

2. Search
```
D.search()
```

3. Download
```
D.download()
```

### tl;dr
```
import dataspace_downloader as dd
D = dd.Downloader("my_parameters.yml")
D.search()
D.download()
```