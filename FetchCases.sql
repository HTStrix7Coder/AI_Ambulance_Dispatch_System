use medicalsystem;
SET SQL_SAFE_UPDATES = 0;
UPDATE cases
SET status = 'Completed'
WHERE id > 0; -- uses primary key
-- optionally re-enable
SET SQL_SAFE_UPDATES = 1;
select * from cases;