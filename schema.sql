CREATE TABLE swimmers (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    gender TEXT NOT NULL,
    cohort_year INTEGER NOT NULL,   
    team TEXT NOT NULL,
    incoming_power_index REAL
);

CREATE TABLE times (
    id INTEGER PRIMARY KEY,
    swimmer_id INTEGER NOT NULL,
    season_id INTEGER NOT NULL,
    team_id INTEGER NOT NULL,
    event_distance INTEGER NOT NULL,
    event_stroke TEXT NOT NULL,
    event_course TEXT NOT NULL,
    event_time TEXT NOT NULL,
    point_value REAL NOT NULL,
    date_of_swim TEXT NOT NULL,
    FOREIGN KEY (swimmer_id) REFERENCES swimmers(id)
);