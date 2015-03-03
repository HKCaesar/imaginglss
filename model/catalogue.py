import numpy
from astropy.io import fits
from columnstore import DiskColumnStore

def coord2xyz(coord):
    RA, DEC = coord
    xyz = numpy.empty(len(RA), ('f4', 3))
    c = numpy.cos(DEC / 180. * numpy.pi)
    xyz[:, 0] = c * numpy.sin(RA / 180. * numpy.pi)
    xyz[:, 1] = c * numpy.cos(RA / 180. * numpy.pi)
    xyz[:, 2] = numpy.sin(DEC / 180. * numpy.pi)
    return xyz.T

class Catalogue(DiskColumnStore):
    """ Catalogue. 

        Only columns that are accessed are loaded to the memory.

        The columns are cached into cachedir, which is initialized 
        by the DataRelease object.

        We assume the catalogue is split into multiple files.
        and the list of file names are provided as an input.
    """
    def __init__(self, cachedir, filenames):
        """ cachedir is the location for caching.
            filenames are a list of fits file names for the EDR
        """
        self.filenames = filenames
        fn = filenames[0]
        first = fits.open(fn)[1].data
        DiskColumnStore.__init__(self, cachedir, first.dtype)

    def fetch(self, column):
        cat = [numpy.array(fits.open(fn)[1].data[column], copy=True)
            for fn in self.filenames]
        cat = numpy.concatenate(cat)
        return cat

    def __repr__(self):
        return 'Catalogue: %s' % str(self.dtype)

    def neighbours(self, coord, sep):
        pass
