from numpy import *

def euler(ai, bi, select=1, fk4=False):
   """
    Transform between Galactic, celestial, and ecliptic coordinates.

    Use the procedure ASTRO to use this routine interactively
   
    Parameters
    ---------- 
    AI : array_like
        Input Longitude in DEGREES, scalar or vector.  If only two
                  parameters are supplied, then  AI and BI will be modified to
                  contain the output longitude and latitude.
    BI : array_like 
        Input Latitude in DEGREES
    SELECT : integer (1-6), optional
        Specifying type of coordinate transformation.
   
        SELECT   From          To        |   SELECT      From            To
          1     RA-Dec (2000)  Galactic   |     4       Ecliptic      RA-Dec
          2     Galactic       RA-DEC     |     5       Ecliptic      Galactic
          3     RA-Dec         Ecliptic   |     6       Galactic      Ecliptic
   
        If not supplied as a parameter or keyword, then EULER will prompt for
        the value of SELECT
        Celestial coordinates (RA, Dec) should be given in equinox J2000
        unless the /FK4 keyword is set.
    FK4 : boolean
        If this keyword is set and non-zero, then input and output
            celestial and ecliptic coordinates should be given in equinox
            B1950.

    Returns
    -------
    AO : array_like
        Output Longitude in DEGREES
    BO : array_like
        Output Latitude in DEGREES
   
    NOTES
    -----
    EULER was changed in December 1998 to use J2000 coordinates as the
    default, ** and may be incompatible with earlier versions***.

    Written W. Landsman,  February 1987
    Adapted from Fortran by Daryl Yentis NRL
    Converted to IDL V5.0   W. Landsman   September 1997
    Made J2000 the default, added /FK4 keyword  W. Landsman December 1998
    Add option to specify SELECT as a keyword W. Landsman March 2003
   """

   n_params = 5
   select1 = select
   
   # ON_ERROR, 2
   
#   print 'Syntax - EULER, AI, BI, A0, B0, [ SELECT, /FK4, SELECT= ]'
#   print '    AI,BI - Input longitude,latitude in degrees'
#   print '    AO,BO - Output longitude, latitude in degrees'
#   print '    SELECT - Scalar (1-6) specifying transformation type'
   
   twopi = 2.0e0 * pi
   fourpi = 4.0e0 * pi
   deg_to_rad = 180.0e0 / pi
   
   #   J2000 coordinate conversions are based on the following constants
   #   (see the Hipparcos explanatory supplement).
   #  eps = 23.4392911111d              Obliquity of the ecliptic
   #  alphaG = 192.85948d               Right Ascension of Galactic North Pole
   #  deltaG = 27.12825d                Declination of Galactic North Pole
   #  lomega = 32.93192d                Galactic longitude of celestial equator
   #  alphaE = 180.02322d              Ecliptic longitude of Galactic North Pole
   #  deltaE = 29.811438523d            Ecliptic latitude of Galactic North Pole
   #  Eomega  = 6.3839743d              Galactic longitude of ecliptic equator
   
   if fk4:   
      equinox = '(B1950)'
      psi = array ([0.57595865315e0, 4.9261918136e0, 0.00000000000e0, 0.0000000000e0, 0.11129056012e0, 4.7005372834e0])
      stheta = array ([0.88781538514e0, -0.88781538514e0, 0.39788119938e0, -0.39788119938e0, 0.86766174755e0, -0.86766174755e0])
      ctheta = array([0.46019978478e0, 0.46019978478e0, 0.91743694670e0, 0.91743694670e0, 0.49715499774e0, 0.49715499774e0])
      phi = array([4.9261918136e0, 0.57595865315e0, 0.0000000000e0, 0.00000000000e0, 4.7005372834e0, 0.11129056012e0])
   else:   
      equinox = '(J2000)'
      psi = array([0.57477043300e0, 4.9368292465e0, 0.00000000000e0, 0.0000000000e0, 0.11142137093e0, 4.71279419371e0])
      stheta = array([0.88998808748e0, -0.88998808748e0, 0.39777715593e0, -0.39777715593e0, 0.86766622025e0, -0.86766622025e0])
      ctheta = array([0.45598377618e0, 0.45598377618e0, 0.91748206207e0, 0.91748206207e0, 0.49714719172e0, 0.49714719172e0])
      phi = array([4.9368292465e0, 0.57477043300e0, 0.0000000000e0, 0.00000000000e0, 4.71279419371e0, 0.11142137093e0])
      
   i = select - 1                         # IDL offset
   a = ai / deg_to_rad - phi[i]
   b = bi / deg_to_rad
   sb = sin(b) ;        cb = cos(b)
   cbsa = cb * sin(a)
   b = -stheta[i] * cbsa + ctheta[i] * sb
   bo = arcsin(minimum(b, 1.0e0)) * deg_to_rad

   a = arctan2(ctheta[i] * cbsa + stheta[i] * sb, cb * cos(a))
   ao = ((a + psi[i] + fourpi) % twopi) * deg_to_rad

   return (ao,bo)
