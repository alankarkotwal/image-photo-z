SELECT ALL
  spec.specObjID AS id,
  spec.z AS redshift,
  spec.zErr as redshiftError,
  spec.ra,
  spec.dec,
  specAll.class,
  specAll.run,
  specAll.camcol,
  specAll.field
INTO mydb.objects_with_redshifts
FROM SpecObj AS spec
JOIN SpecPhotoAll AS specAll
ON spec.specObjID = specAll.specObjID,
  PhotoObj AS phot
WHERE
  specAll.ObjID = phot.ObjID
  AND phot.CLEAN = 1
  AND spec.zWarning = 0
