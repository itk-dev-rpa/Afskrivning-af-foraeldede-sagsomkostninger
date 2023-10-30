# Afskrivning af forældede sagsomkostninger


Outdated fees and interest are to be deleted once a month.
The prerequisite is that they are outdated within Aarhus Municipality, meaning they have not been sent for collection to the Danish Tax Agency (Gældsstyrelsen),
and therefore Aarhus Municipality no longer has a claim to them.

## Configurations
`config.py` contains OpenOrchestrator constant names and SQL schema for the job queue.

## Links
[PDD](https://aarhuskommune.sharepoint.com/:w:/r/Sites/afd-afdsite3229/Delte%20dokumenter/Drift%20%26%20%C3%98konomi/Forretningsudvikling%20og%20debitorstyring/PDD%20(RPA)/PDD%20-%20%20Afskrivning%20af%20for%C3%A6ldede%20sagsonkostninger%202.docx?d=w59fba12fb8634aa6972303b918fc9077&csf=1&web=1&e=85JQ29)

[Reset Opus password](https://portal-k1-nc-22.kmd.dk/webdynpro/resources/kmd.dk/sik~passwordselfservice/PasswordSelfService#)

When the robot is run from OpenOrchestrator the main.bat file is run.
main.bat does a few things:
1. A virtual environment is automatically setup with the required packages.
2. The framework is called passing on all arguments needed by [OpenOrchestratorConnection](https://github.com/itk-dev-rpa/OpenOrchestratorConnection).

## Requirements
Minimum python version 3.10

# Testing 

Run from CMD (main.bat)
```bash
main "test_fosa" "Driver={ODBC Driver 17 for SQL Server};Server=SRVSQLHOTEL03;Database=MKB-ITK-RPA;Trusted_Connection=yes;" "<secret key>"
```

Run from terminal as python process
```python
python run.py "test_fosa" "Driver={ODBC Driver 17 for SQL Server};Server=SRVSQLHOTEL03;Database=MKB-ITK-RPA;Trusted_Connection=yes;" "<secret key>"
```

## Unittest using an existing database
Modify the hard-coded connection string in test_sql_integration.py

## Unittest using Docker
Unittesting the job queue require a database. Steps to launch and configure MSSQL in Docker:

1. local test databse

`docker run -e "ACCEPT_EULA=Y" -e "MSSQL_SA_PASSWORD=password" -p 1433:1433 -d mcr.microsoft.com/mssql/server:2022-latest`

2.  connect to sqlcmd

`docker exec -it objective_mendel /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P password `

3. local setup script to create database and user 

`docker exec objective_mendel bash < ~/mssql.sh`

```sql
create database TestFosa
go

-- Use the newly created database
USE TestFosa;
GO

-- Create a new login
CREATE LOGIN NewUser WITH PASSWORD = 'rf6zgV5H';
GO

-- Create a user for the login in the database
CREATE USER NewUser FOR LOGIN NewUser;
GO

-- Assign permissions (e.g., db_owner role) to the user
EXEC sp_addrolemember 'db_owner', 'NewUser';
GO
```

Validate creation
```sql
SELECT name
FROM sys.databases
WHERE database_id > 4;
```


## Flow

The flow of the framework is sketched up in the following illustration:

![Flow diagram](Robot-Queue-Framework.drawio.svg)
