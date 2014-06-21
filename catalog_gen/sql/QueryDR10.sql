SELECT ALL
  spec.specObjID AS id,
  spec.ra,
  spec.dec,
  spec.z AS redshift,
  spec.zErr as redshiftError,
  specAll.class,
  specAll.run,
  specAll.camcol,
  specAll.field
FROM SpecObj AS spec
JOIN SpecPhotoAll AS specAll
ON spec.specObjID = specAll.specObjID,
  PhotoObj AS phot
WHERE
  specAll.ObjID = phot.ObjID
  AND phot.CLEAN = 1
  AND spec.zWarning = 0
