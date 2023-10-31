TABLE_NAME = "fosa_job_queue"
CREATE_TABLE_QUERY = """(
    id INT IDENTITY(1,1) PRIMARY KEY,
    aftale VARCHAR(20) NOT NULL,
    fp VARCHAR(20) NOT NULL,
    bilag VARCHAR(30) NOT NULL,
    status VARCHAR(255) DEFAULT 'New',
    date_created DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    date_completed DATETIME,    
);
"""