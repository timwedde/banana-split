# banana-split
This script takes a folder of MIDI files and splits them by channel and track.

## Download
* [Master Version](https://github.com/timwedde/banana-split/archive/master.zip)

## Installation
This project uses Python 3.  
It is recommended to use [virtualenv](https://pypi.python.org/pypi/virtualenv) with this project.
```
$ git clone https://github.com/timwedde/banana-split.git
$ cd banana-split
$ virtualenv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```

## Usage
```
$ banana-split.py [-h] -i dir -o dir [-t N] [-k] [-v]

Split MIDI files into channels and tracks.

optional arguments:
  -h, --help            show this help message and exit
  -i dir, --input dir   (required) The folder containing the input data
  -o dir, --output dir  (required) The folder containing the output data
  -t N, --threads N     The amount of threads to use (default: local core count)
  -k, --keep            When given, will keep the intermediary product of each
                        file conversion (.csv)
  -v, --verbose         When given, will produce more verbose output for
                        debugging purposes
```


### Dependencies
* [midicsv](http://www.fourmilab.ch/webtools/midicsv/)
* [tqdm](https://pypi.python.org/pypi/tqdm)

## Contributors

### Contributors on GitHub
* [Contributors](https://github.com/timwedde/banana-split/graphs/contributors)

<!--
### Credit
TBD
-->

## License
* see [LICENSE](https://github.com/timwedde/banana-split/blob/master/LICENSE) file

<!--
## Version
TBD
-->

<!--
## Documentation
TBD
-->
