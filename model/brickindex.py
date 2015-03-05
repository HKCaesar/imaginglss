import numpy

from astropy.io import fits
from brick import Brick

class BrickIndex(object):
    def __init__(self, brickdata):
        """ 
            indexing bricks from bricks.fits 
            bricks = fits.open('bricks.fits')
            bi = BrickIndex(bricks[1].data) 

            brickdata can also be a file name.
        """
        if isinstance(brickdata, basestring):
            brickdata = fits.open(brickdata)[1].data[:]
            
        self.brickdata = numpy.array(brickdata[:], copy=True)
        self.ncols = numpy.bincount(brickdata['BRICKROW'])

        self.ROWMAX = brickdata['BRICKROW'].max()
        self.COLMAX = brickdata['BRICKCOL'].max() 

        # fast querying from row col
        self.hash = brickdata['BRICKROW'] * (self.COLMAX + 1) + brickdata['BRICKCOL']

        self.RA = self.brickdata['RA']
        self.DEC = self.brickdata['DEC']
        self.RA1 = self.brickdata['RA1']
        self.DEC1 = self.brickdata['DEC1']
        self.RA2 = self.brickdata['RA2']
        self.DEC2 = self.brickdata['DEC2']

        assert (self.brickdata['BRICKID'] == numpy.arange(len(self.brickdata)) + 1).all()

    def get_brick(self, index):
        """ create a single brick from bid """
        # template header to feed wcs
        # fill CRVAL1, CRVAL2 later
        return Brick(self.brickdata['BRICKID'][index], 
                self.brickdata['BRICKNAME'][index], 
                self.brickdata['RA'][index], 
                self.brickdata['DEC'][index], 
                self.brickdata['RA1'][index], 
                self.brickdata['RA2'][index], 
                self.brickdata['DEC1'][index], 
                self.brickdata['DEC2'][index])

    def query(self, coord):
        """ 
            querying the indices for given RA and DEC
            RA, DEC = coord

            coord shall be in the same coordinate system of the bricks.

            returns the internal index of the bricks (differ from BRICKID.

            Get real Brick objects by iterating over the result and use get_brick(i)
        """
        RA, DEC = coord
        RA = numpy.asarray(RA)
        DEC = numpy.asarray(DEC)
        row = numpy.int32(numpy.floor(DEC * self.ROWMAX / 180 + 360. + 0.5))
        row = numpy.clip(row, 0, self.ROWMAX)
        ncols = self.ncols[row]
        col = numpy.int32(numpy.floor(RA * ncols / 360. ))
        hash = row * (self.COLMAX + 1) + col
        ind = self.hash.searchsorted(hash)
        return ind

    def optimize(self, coord):
        """ optimize the ordering of ra, dec,

            This will sort ra, dec by their brickid.

            return sorted_ra, sorted_dec, invert_arg

            invariance:
                sorted_ra[inverg_arg] == ra
                sorted_dec[inverg_arg] == dec
        """
        coord = numpy.array(coord)
        bid = self.query(coord)
        arg = bid.argsort()

        invarg = numpy.empty_like(arg)
        invarg[arg] = numpy.arange(len(arg), dtype='i8')
        return numpy.array(coord[:, arg]), invarg


