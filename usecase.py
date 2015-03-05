from model.datarelease import DataRelease
import numpy

dr = DataRelease(version='EDR')

brick = dr.observed_bricks[0]
print dr.images['z']['IMAGE'].metadata(brick)
#print dr.images['DEPTH'].open(brick, band='z')
#print brick

def test398599():
    """ test image readout on brick-398599. 
    """
    dr = DataRelease(version='EDR')
    brick = dr.observed_bricks[0]
    dr.images['z']['IMAGE'].preload([brick])

    img2 = dr.images['z']['IMAGE'].open(brick)
    assert (img2[300:-300, 300:-300] != 0).any()

    print 'Testing on', brick
    print dr.images['z']['IMAGE'].get_filename(brick)
    x, y = numpy.indices((3600, 3600))
    x = numpy.ravel(x) + 0.5
    y = numpy.ravel(y) + 0.5
    coord = brick.revert((x, y))

    x2, y2 = brick.query(coord)
    print x, x2
    print y, y2
    assert numpy.allclose(x, x2)
    assert numpy.allclose(y, y2)


    img3 = brick.readout(coord, dr.images['z']['IMAGE'])
    diff = img3.reshape(3600, 3600) - img2
    assert (diff[300:-300, 300:-300] == 0).all()


    img = dr.readout(coord, dr.images['z']['IMAGE'])
    print 'brick readout passed'
    print 'found', (~numpy.isnan(img)).sum()
    diff = img.reshape(3600, 3600) - img2
    assert (diff[300:-300, 300:-300] == 0).all()
    print 'dr readout passed'


def testrandom():
    dr = DataRelease(version='EDR')

    print dr.footprint
    u1, u2 = numpy.random.random(size=(2, 4))
    RA = (dr.footprint.ramax - dr.footprint.ramin) * u1 + dr.footprint.ramin
    a = 0.5 * ((numpy.cos(dr.footprint.decmax / 180. * numpy.pi)  + 1))
    b = 0.5 * ((numpy.cos(dr.footprint.decmin / 180. * numpy.pi)  + 1))
    u2 = (a - b) * u2 + b
    
    DEC = numpy.arccos(2.0 * u2 - 1) * (180. / numpy.pi)

#    print 'prefetched'
    coord = (RA, DEC)
    print coord
    depth = dr.readout(coord, dr.images['r']['DEPTH'])
    print depth
 
def testcat():
    dr = DataRelease(version='EDR')
    print dr.catalogue 
    print dr.catalogue['RA']
#testrandom()
#testcat()
test398599()
