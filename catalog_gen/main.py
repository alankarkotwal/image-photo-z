#!/usr/bin/python

# Alankar Kotwal

import pysex as ps

cat=ps.run("tests/u.fits", params=['X_IMAGE', 'Y_IMAGE', 'FLUX_APER'])

print cat
