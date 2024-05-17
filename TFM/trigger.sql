CREATE TRIGGER aplicacion_customuser AFTER
UPDATE
ON 
aplicacion_customuser
FOR EACH ROW 
WHEN (new.status = 'Paid')
EXECUTE PROCEDURE aplicacion_customuser();