import sqlite3

def setup_database():
    conn = sqlite3.connect('event_management.db')
    cursor = conn.cursor()
    
    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS Kravtsov_Events (
            event_id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_name TEXT NOT NULL,
            event_type TEXT NOT NULL CHECK (event_type IN ('sports', 'music', 'exhibition')),
            event_start TIMESTAMP NOT NULL,
            event_end TIMESTAMP NOT NULL,
            event_holder TEXT NOT NULL
            CHECK (event_end > event_start)
        );

        CREATE TABLE IF NOT EXISTS Kravtsov_Users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE CHECK (email LIKE '%@%.%')
        );

        CREATE TABLE IF NOT EXISTS Kravtsov_Tickets (
            ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id INTEGER NOT NULL,
            user_id INTEGER,
            ticket_type TEXT NOT NULL CHECK (ticket_type IN ('one_day', 'multiple_days')),
            seat TEXT NOT NULL CHECK (seat IN ('sitting', 'sitting_vip', 'standing', 'standing_vip')),
            status TEXT NOT NULL DEFAULT 'unsold' CHECK (status IN ('unsold', 'sold', 'expired')),
            FOREIGN KEY (event_id) REFERENCES Kravtsov_Events(event_id),
            FOREIGN KEY (user_id) REFERENCES Kravtsov_Users(user_id)
        );

        CREATE TABLE IF NOT EXISTS Kravtsov_Staff (
            staff_id INTEGER PRIMARY KEY AUTOINCREMENT,
            staff_name TEXT NOT NULL,
            staff_email TEXT NOT NULL UNIQUE check (staff_email LIKE '%@%.%'),
            phone_number TEXT NOT NULL,
            position TEXT NOT NULL,
            schedule_start TEXT NOT NULL,
            schedule_end TEXT NOT NULL,
            salary REAL NOT NULL,
            CHECK (schedule_start LIKE '__:__'),
            CHECK (schedule_end LIKE '__:__')
        );
                        
        CREATE TABLE IF NOT EXISTS Kravtsov_Facilities_Staff (
            facility_id INTEGER NOT NULL,
            staff_id INTEGER NOT NULL,
            FOREIGN KEY (facility_id) REFERENCES Kravtsov_Facilities(facility_id),
            FOREIGN KEY (staff_id) REFERENCES Kravtsov_Staff(staff_id)
        );
                         
        CREATE TABLE IF NOT EXISTS Kravtsov_Facilities (
            facility_id INTEGER PRIMARY KEY AUTOINCREMENT,
            facility_name TEXT NOT NULL,
            facility_status TEXT NOT NULL CHECK (facility_status IN ('free', 'occupied', 'private'))
        );
                         
        CREATE TABLE IF NOT EXISTS Kravtsov_Facilities_Events (
            facility_id INTEGER NOT NULL,
            event_id INTEGER NOT NULL,
            usage_start TIMESTAMP NOT NULL,
            usage_end TIMESTAMP NOT NULL,
            FOREIGN KEY (facility_id) REFERENCES Kravtsov_Facilities(facility_id),
            FOREIGN KEY (event_id) REFERENCES Kravtsov_Staff(event_id)
        );

        CREATE TABLE IF NOT EXISTS Kravtsov_Equipment (
            item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT NOT NULL,
            item_status TEXT NOT NULL CHECK (item_status IN ('free', 'occupied'))
        );
                         
        CREATE TABLE IF NOT EXISTS Kravtsov_Equipment_Events (
            item_id INTEGER NOT NULL,
            event_id INTEGER NOT NULL,
            usage_start TIMESTAMP NOT NULL,
            usage_end TIMESTAMP NOT NULL,
            FOREIGN KEY (item_id) REFERENCES Kravtsov_Equipment(item_id),
            FOREIGN KEY (event_id) REFERENCES Kravtsov_Events(event_id)
        );

        CREATE TABLE IF NOT EXISTS Kravtsov_Security (
            sec_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            sec_item_name TEXT NOT NULL,
            sec_item_status TEXT NOT NULL CHECK (sec_item_status IN ('up', 'out_of_service', 'under_maintenance')),
            facility_id INTEGER NOT NULL,
            FOREIGN KEY (facility_id) REFERENCES Kravtsov_Facilities(facility_id)
        );
    ''')
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    setup_database()