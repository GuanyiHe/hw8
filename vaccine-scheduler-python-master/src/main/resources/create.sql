-- CREATE TABLE Caregivers (
--     Username varchar(255),
--     Salt BINARY(16),
--     Hash BINARY(16),
--     PRIMARY KEY (Username)
-- );

-- CREATE TABLE Availabilities (
--     Time date,
--     Username varchar(255) REFERENCES Caregivers,
--     PRIMARY KEY (Time, Username)
-- );

-- CREATE TABLE Vaccines (
--     Name varchar(255),
--     Doses int,
--     PRIMARY KEY (Name)
-- );

-- CREATE TABLE Patient (
--     Username varchar(255),
--     Salt BINARY(16),
--     Hash BINARY(16),
--     PRIMARY KEY (Username)
-- );


-- CREATE TABLE Appointment(
--     Appointmentid INT IDENTITY(1,1),
--     patientname VARCHAR(255) REFERENCES Patient(Username),
--     Vaccinesname VARCHAR(255) REFERENCES Vaccines(Name),
--     PRIMARY KEY(Appointmentid)
-- );


-- CREATE TABLE Appointmentcheck(
--     Time date,
--     Username VARCHAR(255),
--     Appointmentid INT UNIQUE REFERENCES Appointment(Appointmentid),
--     FOREIGN KEY (Time, Username) REFERENCES Availabilities(Time, Username),
--     UNIQUE(Time, Username)
-- );

