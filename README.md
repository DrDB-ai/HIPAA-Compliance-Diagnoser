# HIPAA Compliance Checker

This repository contains code for checking HIPAA compliance for different database management systems (DBMS).

## Supported Databases

The HIPAA compliance checks are implemented for the following database management systems:

- PostgreSQL
- MySQL
- Microsoft SQL Server
- IBM Db2
- Oracle Database

## HIPAA Compliance Checks

### Sensitive Data Scan

This check scans the database for columns containing sensitive data related to patients, such as names, addresses, or medical history.

### Access Control Check

This check examines the database's access controls to ensure that only authorized users have access to patient data.

### Audit Trail Check

This check verifies the existence of an audit trail mechanism in the database to track access and modifications to patient data.

### Encryption Check

This check verifies if encryption is enabled in the database to protect patient data at rest.

### Database Activity Monitoring Check

This check verifies if database activity monitoring is enabled to detect unauthorized access or suspicious activities related to patient data.

## Installation

To run the HIPAA compliance checks, you'll need to have Python installed on your system. Clone this repository to your local machine:

```bash
git clone https://github.com/DrDB-ai/db_hipaa_compliance_report.git
```

## Docker

### Build

```
docker build --platform=linux/amd64  -t db-hipaa-compliance-report .
```

### Run

```
docker run --platform=linux/amd64 -p 8501:8501 db-hipaa-compliance-report  
```

## Contributing

Contributions are welcome! If you'd like to add additional HIPAA compliance checks or improve existing ones, feel free to fork this repository, make your changes, and submit a pull request.