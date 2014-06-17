SELECT ALL
  objs.id,
  objs.ra,
  objs.dec,
  objs.redshift,
  objs.redshiftError,
  objs.class,
  objs.run,
  objs.camcol,
  objs.field
INTO mydb.one_square_degree
FROM mydb.objects_with_redshifts AS objs
WHERE
  objs.ra>180 AND objs.ra<181
  AND objs.dec>45 AND objs.dec<46
