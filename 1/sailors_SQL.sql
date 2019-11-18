USE sailors;
SELECT s.sid, s.sname, s.rating, s.age, m.bid FROM sailors AS s, (SELECT bid, sid, MAX(total) FROM (SELECT bid, sid, count(*) AS total FROM reserves GROUP BY sid,bid ORDER BY bid ASC, total DESC) AS t GROUP BY bid) AS m WHERE s.sid = m.sid;
SELECT b.bid, b.bname, COUNT(*) FROM boats AS b, reserves AS r WHERE b.bid = r.bid GROUP BY b.bid;
SELECT s.sid, s.sname FROM reserves AS r, sailors AS s WHERE r.sid = s.sid AND r.bid IN (SELECT b.bid FROM boats AS b WHERE b.color = 'red') GROUP BY r.sid HAVING COUNT(DISTINCT r.bid) = (SELECT COUNT(b.bid) FROM boats AS b WHERE b.color = 'red');
SELECT s.sid, s.sname, s.rating, s.age FROM sailors AS s, reserves AS r, boats AS b WHERE s.sid = r.sid AND r.bid = b.bid AND b.color = 'red';
SELECT b.bid, b.bname, b.color, b.length, count(*) FROM reserves AS r, boats AS b WHERE r.bid= b.bid GROUP BY r.bid ORDER BY count(*) DESC LIMIT 1;
SELECT s.sid, s.sname, s.rating, s.age FROM sailors AS s, reserves AS r, boats AS b WHERE s.sid = r.sid AND r.bid = b.bid AND b.color <> 'red';
SELECT rating, AVG(age) FROM sailors WHERE rating=10;