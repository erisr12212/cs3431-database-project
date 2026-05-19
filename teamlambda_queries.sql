-- Team Name: teamlambda
-- Members: David Ramos, Eris Ropi, Benjamin McAuliffe

--Q1:
SELECT DISTINCT BC.categoryname
FROM business
INNER JOIN business_category BC on BC.businessid = business.businessid
WHERE business.city = 'Scottsdale' AND business.state = 'AZ';


SELECT DISTINCT BA.attributename
FROM business
INNER JOIN business_attribute BA on BA.businessid = business.businessid
WHERE business.city = 'Scottsdale' AND business.state = 'AZ';


--Q2:
SELECT Businessid, name, streetaddress, num_tips
FROM Business B
WHERE EXISTS (
   SELECT *
   FROM business_category BC
   WHERE BC.categoryname = 'Restaurants' AND BC.businessid = B.businessid
) AND EXISTS (
   SELECT *
   FROM business_category BC
   WHERE BC.categoryname = 'Breakfast & Brunch' AND BC.businessid = B.businessid
) AND EXISTS (
   SELECT *
   FROM business_category BC
   WHERE BC.categoryname = 'Bakeries' AND BC.businessid = B.businessid
) AND B.city = 'Scottsdale' AND B.state = 'AZ'
ORDER BY B.name;


--Q3:
SELECT B.businessid, B.name, B.streetaddress, B.num_tips
FROM business B
WHERE B.city = 'Scottsdale' AND B.state = 'AZ'
 AND EXISTS (
   SELECT *
   FROM business_attribute BA
   WHERE BA.attributename = 'BusinessAcceptsCreditCards' AND BA.businessid = B.businessid
   AND BA.value = 'True'
) AND EXISTS (
   SELECT *
   FROM business_attribute BA
   WHERE BA.attributename = 'ByAppointmentOnly' AND BA.businessid = B.businessid
   AND BA.value = 'True'
) AND EXISTS (
   SELECT *
   FROM business_attribute BA
   WHERE BA.attributename = 'WiFi' AND BA.businessid = B.businessid
   AND BA.value = 'free'
) ORDER BY B.name;


--Q4:
SELECT B.businessid, B.name, B.streetaddress, B.num_tips
FROM business B
WHERE B.city = 'Scottsdale' AND B.state = 'AZ'
 AND EXISTS (
   SELECT *
   FROM business_attribute BA
   WHERE BA.attributename = 'BusinessAcceptsCreditCards' AND BA.businessid = B.businessid
   AND BA.value = 'True'
) AND EXISTS (
   SELECT *
   FROM business_attribute BA
   WHERE BA.attributename = 'RestaurantsPriceRange2' AND BA.businessid = B.businessid
   AND BA.value = '2'
) AND EXISTS (
   SELECT *
   FROM business_attribute BA
   WHERE BA.attributename = 'WiFi' AND BA.businessid = B.businessid
   AND BA.value = 'free'
) AND EXISTS (
   SELECT *
   FROM business_category BC
   WHERE BC.categoryname = 'Restaurants' AND BC.businessid = B.businessid
) AND EXISTS (
   SELECT *
   FROM business_category BC
   WHERE BC.categoryname = 'Breakfast & Brunch' AND BC.businessid = B.businessid
) AND EXISTS (
   SELECT *
   FROM business_category BC
   WHERE BC.categoryname = 'Bakeries' AND BC.businessid = B.businessid
) AND EXISTS (
   SELECT *
   FROM schedule S
   WHERE S.day = 'Monday' AND S.open <= CAST('10:30' AS TIME) AND S.close >= CAST('13:30' AS TIME)
   AND S.businessid = B.businessid
)
ORDER BY B.name;


--Q5:
CREATE OR REPLACE FUNCTION count_categories(b1 TEXT, b2 TEXT) RETURNS integer
AS $$
   DECLARE result integer;
   BEGIN
   SELECT COUNT(BCN.categoryname) INTO result
FROM ((SELECT categoryname
FROM business_category BC1
WHERE BC1.businessid = $1)
INTERSECT
(SELECT categoryname
FROM business_category BC2
WHERE BC2.businessid = $2)) BCN;
   RETURN result;
   END
   $$ LANGUAGE plpgsql;
--Function test
SELECT count_categories('iPPzDL_oY8SJCjmycuXcVg', 'ncXQtqJT5Gk1QztwTrBrgw');


--Q6:
CREATE OR REPLACE FUNCTION geodistance(lat1 double precision, lon1 double precision,
                                      lat2 double precision, lon2 double precision)
RETURNS double precision AS $$
DECLARE
   r double precision;
   dlat double precision;
   dlon double precision;
   a double precision;
   c double precision;
BEGIN
   r := 3959.0;  -- Earth’s radius in miles
   dlat := radians(lat2 - lat1);
   dlon := radians(lon2 - lon1);
   a := sin(dlat/2) * sin(dlat/2)
      + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2) * sin(dlon/2);
   c := 2 * atan2(sqrt(a), sqrt(1 - a));
   RETURN r * c;
END;
$$ LANGUAGE plpgsql;


-- test: should be ~12.557912
SELECT geodistance(33.6399735577, -112.1334044052, 33.5796797, -111.9275444);


--Q7:

SELECT b1.BusinessId, b1.Name, b2.City, b2.ZIP,
      b2.BusinessId, b2.Name,
      count_categories(b1.BusinessId, b2.BusinessId) AS rank
FROM business b1, business b2
WHERE b1.BusinessId = 'iPPzDL_oY8SJCjmycuXcVg'
 AND b1.BusinessId <> b2.BusinessId
 AND b1.ZIP = b2.ZIP
 AND geodistance(b1.Latitude, b1.Longitude, b2.Latitude, b2.Longitude) <= 20
 AND count_categories(b1.BusinessId, b2.BusinessId) > 0
ORDER BY rank DESC
LIMIT 15;


--Q8:
SELECT b.BusinessId, b.Name, b.StreetAddress, b.num_tips
FROM business b
JOIN business_category bc ON bc.BusinessId = b.BusinessId
WHERE b.ZIP = '85251'
AND bc.CategoryName = 'Restaurants'
AND b.num_tips = (SELECT MAX(b2.num_tips)
                 FROM business b2
                 JOIN business_category bc2 ON bc2.BusinessId = b2.BusinessId
                 WHERE b2.ZIP = '85251'
                 AND bc2.CategoryName = 'Restaurants'
                 );

--Q9:
SELECT u.Name AS user_name, t.tip_date AS tipdate, t.tip_Text AS tiptext
FROM friends f, users u, tip t
WHERE f.UserId1 = 'TiWF94rl8Q6jqQf2YZSFPA'
 AND u.UserId = f.UserId2
 AND t.UserId = f.UserId2
ORDER BY t.tip_date DESC
LIMIT 1;

--Q10:
SELECT u.UserId AS friendsid, u.Name AS friendsname,
      to_char(t.tip_date, 'YYYY/MM/DD HH24:MI') AS to_char,
      t.tip_Text AS tiptext
FROM friends f, users u, tip t
WHERE f.UserId1 = 'TiWF94rl8Q6jqQf2YZSFPA'
 AND u.UserId = f.UserId2
 AND t.UserId = f.UserId2
 AND t.tip_date = (SELECT MAX(t2.tip_date)
                   FROM tip t2
                   WHERE t2.UserId = f.UserId2)
ORDER BY t.tip_date DESC;

--Q11:
CREATE OR REPLACE FUNCTION assignNewTips() RETURNS trigger AS '


BEGIN
   UPDATE business
   SET num_tips = num_tips + 1
   WHERE NEW.BusinessId = business.BusinessId;


   UPDATE users
   SET tip_count = tip_count + 1
   WHERE NEW.UserId = users.UserId;


    RETURN NEW;
END
' LANGUAGE plpgsql;


CREATE or REPLACE TRIGGER updateTips
AFTER INSERT ON tip
FOR EACH ROW
EXECUTE FUNCTION assignNewTips();


SELECT num_tips
FROM business
WHERE BusinessId = 'dQj5DLZjeDK3KFysh1SYOQ';


SELECT tip_count
FROM users
WHERE UserId = '_DaFdmq0gtXf1spn1qC_1Q';


INSERT INTO tip (UserId, BusinessId, tip_date, Likes, tip_Text)
VALUES ('_DaFdmq0gtXf1spn1qC_1Q', 'dQj5DLZjeDK3KFysh1SYOQ', '2026-09-21 12:00:00', 0, 'Test tip');


SELECT num_tips
FROM business
WHERE BusinessId = 'dQj5DLZjeDK3KFysh1SYOQ';


SELECT tip_count
FROM users
WHERE UserId = '_DaFdmq0gtXf1spn1qC_1Q';


--Q12:



--12
CREATE OR REPLACE FUNCTION entranceMessage() RETURNS trigger AS '


BEGIN
   IF NOT EXISTS (SELECT *
       FROM schedule s
       WHERE s.BusinessId = NEW.BusinessId
       AND s.day = TRIM(TO_CHAR(NEW.timestamp, ''Day''))
       AND s.Open <= NEW.timestamp::TIME
       AND s.Close >= NEW.timestamp::TIME)  THEN
   RAISE EXCEPTION ''Business is not currently open'';


   end if;




    RETURN NEW;
END
' LANGUAGE plpgsql;


CREATE or REPLACE TRIGGER checkEntrance
BEFORE INSERT ON checkin
FOR EACH ROW
EXECUTE FUNCTION entranceMessage();


-- won't raise error
INSERT INTO checkin (BusinessId, timestamp)
VALUES ('gnKjwL_1w79qoiV3IC_xQQ', '2026-04-20 18:00:00');


--Trying to check in to business that is closed, will raise error
INSERT INTO checkin (BusinessId, timestamp)
VALUES ('gnKjwL_1w79qoiV3IC_xQQ', '2026-04-20 10:00:00');

