-- Team Name: teamlambda
-- Members: Eris Ropi, David Phoneramos, Benjamin Mcauliffe


--PART A
CREATE INDEX idx_tip_businessid ON tip(BusinessId);

UPDATE business b
SET num_tips = (SELECT COUNT(*)
                FROM tip
                WHERE tip.BusinessId = b.BusinessId
);

CREATE INDEX idx_tip_userid ON tip(UserId);

CREATE TEMP TABLE user_tip_counts AS
SELECT UserId, COUNT(*) AS cnt
FROM tip
GROUP BY UserId;

UPDATE users u
SET tip_count = utc.cnt
FROM user_tip_counts utc
WHERE u.UserId = utc.UserId;

DROP TABLE user_tip_counts;


--PART B
SELECT b.BusinessId, b.num_tips, COUNT(t.BusinessId)  AS actual_count
FROM Business b
JOIN tip t ON t.BusinessId = b.BusinessId
WHERE b.BusinessId = 'dQj5DLZjeDK3KFysh1SYOQ'
GROUP by b.BusinessId, b.num_tips;

SELECT u.UserId, u.tip_count, COUNT(t.UserId)  AS actual_count
FROM users u
JOIN tip t ON t.UserId = u.UserId
WHERE u.UserId = '_DaFdmq0gtXf1spn1qC_1Q'
GROUP by u.UserId, u.tip_count;





