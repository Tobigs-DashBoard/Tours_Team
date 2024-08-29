CREATE_PACKAGES = '''
CREATE TABLE Packages (
    PRIMARY KEY package_id VARCHAR(50),
    package_name VARCHAR(255),
    duration VARCHAR(50),
    start_date DATE,
    end_date DATE,
    price_original INTEGER,
)
'''

CREATE_FLIGHTS = '''
CREATE TABLE Flights (
    package_name VARCHAR(255)
    departure_city VARCHAR(100),
    departure_time DATETIME,
    arrival_city VARCHAR(100),
    arrival_time DATETIME,
    flight_number VARCHAR(50),
    airline VARCHAR(100),
    PRIMARY KEY (package_name, flight_number)
    FOREIGN KEY (package_name) REFERENCES Packages(package_name)
)
'''

CREATE_HOTELS = '''
CREATE TABLE Hotels (
    package_name VARCHAR(255),
    hotel_name VARCHAR(255),
    hotel_address VARCHAR(255),
    check_in_date DATE,
    check_out_date DATE,
    day INTEGER,
    PRIMARY KEY (package_name, day),
    FOREIGN KEY (package_name) REFERENCES Packages(package_name)
)
'''

CREATE_INTINERARY = '''
CREATE TABLE Itinerary (
    package_name VARCHAR(255),
    day INTEGER,
    date DATE,
    city VARCHAR(100),
    activities_title VARCHAR(255),
    PRIMARY KEY (package_name, day),
    FOREIGN KEY (package_name) REFERENCES Packages(package_name)
)
'''

CREATE_INCLUSIONS = '''
CREATE TABLE Inclusions (
    package_name VARCHAR(255),
    adult INTEGER,
    child INTEGER,
    baby INTEGER,
    PRIMARY KEY (package_name),
    FOREIGN KEY (package_name) REFERENCES Packages(package_name)
)
'''

INSERT_PACKAGE = """
INSERT INTO Packages
(package_id, package_name, duration, start_date, end_date, price_original)
VALUES (%s, %s, %s, %s, %s, %s)
ON DUPLICATE KEY UPDATE
package_name = VALUES(package_name),
duration = VALUES(duration),
start_date = VALUES(start_date),
end_date = VALUES(end_date),
price_original = VALUES(price_original);
"""

INSERT_FLIGHT = """
INSERT INTO Flights
(package_name, departure_city, departure_time, arrival_city, arrival_time, flight_number, airline)
VALUES (%s, %s, %s, %s, %s, %s, %s)
ON DUPLICATE KEY UPDATE
departure_city = VALUES(departure_city),
departure_time = VALUES(departure_time),
arrival_city = VALUES(arrival_city),
arrival_time = VALUES(arrival_time),
airline = VALUES(airline);
"""

INSERT_HOTEL = """
INSERT INTO Hotels
(package_name, hotel_name, hotel_address, check_in_date, check_out_date, day)
VALUES (%s, %s, %s, %s, %s, %s)
ON DUPLICATE KEY UPDATE
hotel_name = VALUES(hotel_name),
hotel_address = VALUES(hotel_address),
check_in_date = VALUES(check_in_date),
check_out_date = VALUES(check_out_date);
"""

INSERT_ITINERARY = """
INSERT INTO Itinerary
(package_name, day, date, city, activities_title)
VALUES (%s, %s, %s, %s, %s)
ON DUPLICATE KEY UPDATE
date = VALUES(date),
city = VALUES(city),
activities_title = VALUES(activities_title);
"""

INSERT_INCLUSION = """
INSERT INTO Inclusions
(package_name, adult, child, baby)
VALUES (%s, %s, %s, %s)
ON DUPLICATE KEY UPDATE
adult = VALUES(adult),
child = VALUES(child),
baby = VALUES(baby);
"""
