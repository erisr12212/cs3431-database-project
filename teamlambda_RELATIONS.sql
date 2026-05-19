DROP TABLE IF EXISTS friends;
DROP TABLE IF EXISTS business_attribute;
DROP TABLE IF EXISTS business_category;
DROP TABLE IF EXISTS tip;
DROP TABLE IF EXISTS checkin;
DROP TABLE IF EXISTS schedule;
DROP TABLE IF EXISTS attribute;
DROP TABLE IF EXISTS category;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS business;

CREATE TABLE business(
   BusinessId CHAR(22),
   Name VARCHAR,
   StreetAddress VARCHAR,
   City VARCHAR,
   State CHAR(2),
   ZIP CHAR(5),
   Latitude FLOAT,
   Longitude FLOAT,
   Stars FLOAT,
   num_tips INTEGER DEFAULT 0,
   IsOpen INTEGER,
   PRIMARY KEY(BusinessId)
);

CREATE TABLE users(
   UserId CHAR(22),
   Name VARCHAR,
   Stars FLOAT,
   Funny INTEGER,   Cool INTEGER,
   Useful INTEGER,
   Fans INTEGER,
   tip_count INTEGER DEFAULT 0,
   CreatedAt TIMESTAMP,
   PRIMARY KEY(UserId)
);

CREATE TABLE schedule(
   BusinessId CHAR(22),
   Day CHAR(9),
   Open TIME,
   Close TIME,
   PRIMARY KEY(Day, BusinessId),
   FOREIGN KEY(BusinessId) REFERENCES business(BusinessId)
);

CREATE TABLE checkin(
   BusinessId CHAR(22),
   timestamp TIMESTAMP,
   PRIMARY KEY(BusinessId, timestamp),
   FOREIGN KEY(BusinessId) REFERENCES business(BusinessId)
);

CREATE TABLE tip(
   UserId CHAR(22),
   BusinessId CHAR(22),
   tip_date TIMESTAMP,
   Likes INTEGER,
   tip_Text VARCHAR,
   PRIMARY KEY(UserId, BusinessId, tip_date),
   FOREIGN KEY(UserId) REFERENCES users(UserId),
   FOREIGN KEY(BusinessId) REFERENCES business(BusinessId)
);

CREATE TABLE category(
   CategoryName VARCHAR,
   PRIMARY KEY(CategoryName)
);

CREATE TABLE business_category(
   CategoryName VARCHAR,
   BusinessId CHAR(22),
   PRIMARY KEY(CategoryName, BusinessId),
   FOREIGN KEY(BusinessId) REFERENCES business(BusinessId),
   FOREIGN KEY(CategoryName) REFERENCES category(CategoryName)
);

CREATE TABLE attribute(
   AttributeName VARCHAR,
   PRIMARY KEY(AttributeName)
);

CREATE TABLE business_attribute(
   AttributeName VARCHAR,
   Value VARCHAR,
   BusinessId CHAR(22),
   PRIMARY KEY(AttributeName, BusinessId),
   FOREIGN KEY(AttributeName) REFERENCES attribute(AttributeName),
   FOREIGN KEY(BusinessId) REFERENCES business(BusinessId)
);

CREATE TABLE friends(
   UserId1 CHAR(22),
   UserId2 CHAR(22),
   PRIMARY KEY(UserId1, UserId2),
   FOREIGN KEY(UserId1) REFERENCES users(UserId),
   FOREIGN KEY(UserId2) REFERENCES users(UserId)
);

--Need to ensure we don't store friendships 2 times with UserID1:A UserID2:B and also UserID1:B UserID2:A
