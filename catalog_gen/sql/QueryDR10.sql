SELECT TOP 10
  spec.specObjID AS id,
  spec.ra,
  spec.dec,
  spec.z AS redshift,
  spec.zErr AS redshiftError,
  specAll.class,
  specAll.run,
  specAll.camcol,
  specAll.field,
  specAll.dered_u AS u,
  specAll.dered_g AS g,
  specAll.dered_r AS r,
  specAll.dered_i AS i,
  specAll.dered_z AS z
INTO objects_with_redshifts
FROM SpecObj AS spec
JOIN SpecPhotoAll AS specAll
ON spec.specObjID = specAll.specObjID,
  PhotoObj AS phot
WHERE
  specAll.ObjID = phot.ObjID
  AND phot.CLEAN = 1
  AND spec.zWarning = 0
