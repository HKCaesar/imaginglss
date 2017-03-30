
from __future__ import print_function
import numpy as np
import h5py

from imaginglss             import DECALS
from imaginglss.model             import dataproduct
from imaginglss.analysis    import completeness
from imaginglss.utils       import output
from imaginglss.model.ccdtable import CCDTable

from imaginglss.cli import CLI
from kdcount.sphere import points

cli = CLI("Query completeness",
        enable_target_plugins=True,
        enable_confidence=True,
        enable_tycho_veto=True)

cli.add_argument("query",
        help="catalogue to query ccd systematic")

cli.add_argument("ccdfile",
        help="survey ccd fits file; this is the path to the -decals file. we also need the -nondecals and -extras file.")

cli.add_argument("ccdattr", type=lambda x: x.upper(),
        help="column name to query ")

ns = cli.parse_args()
decals = DECALS(ns.conf)

np.seterr(divide='ignore', invalid='ignore')

def main():
    ccdtable = CCDTable(ns.ccdfile)

    ccdtree = points(ccdtable.RA, ccdtable.DEC).tree
    with h5py.File(ns.query) as ff:
        RA = ff['RA'][:]
        DEC = ff['DEC'][:]

    print("size of query is %d" % len(RA))
    print("number of CCDS is %d" % len(ccdtable))

    if ns.ccdattr not in ccdtable.data.dtype.names and ns.ccdattr != 'NEXP':
        raise RuntimeError("ccdattr not found, available ones are %s"
                    % str(list(ccdtable.data.dtype.names) + ['NEXP']))
        
    r1 = np.zeros_like(RA)
    r2 = np.zeros_like(RA)
    N = np.zeros_like(RA)

    querytree = points(RA, DEC).tree
    
    def process(r, i, j):
        mask = ccdtable.query_inside(i, RA[j], DEC[j])
        i = i[mask]
        j = j[mask]

        if ns.ccdattr != 'NEXP':
            v = ccdtable.data[ns.ccdattr][i]
            np.add.at(r1, j, v)
            np.add.at(r2, j, v ** 2)
        np.add.at(N, j, 1)

    ccdtree.root.enum(querytree.root, np.radians(0.2), process)

    COLUMNNAME = 'CCD-%s' % ns.ccdattr

    if ns.ccdattr != 'NEXP':
        r1 /= N
    else:
        r1 = N

    print('mean and std of %s from the query is %g %g' % (ns.ccdattr, r1.mean(), r1.std()))

    with h5py.File(ns.query, 'r+') as ff:
        if COLUMNNAME in ff:
            del ff[COLUMNNAME]
        ds = ff.create_dataset(COLUMNNAME, data=r1)
        ds.attrs.update(cli.prune_namespace(ns))

    print('written as %s in %s' % ( COLUMNNAME, ns.query))

if __name__ == "__main__":
    main()
