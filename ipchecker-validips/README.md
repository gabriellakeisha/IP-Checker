# IPChecker - Total valid IP addresses
python microservice to validate and count valid IPv4 and IPv6 addresses.

## Features
- validates IPv4 addresses (4 groups separated by dots)
- validates IPv6 addresses (2-8 groups separated by colons)
- returns detailed validation results
- unit tests included
- CI pipeline with GitLab

## API Endpoint
### GET /
validates IP addresses and returns count of valid ones.

**Parameters:**
- `items` (required): comma-separated list of IP addresses

**Run locally:**
- install all requirements
- docker
- Example test: http://localhost:5000/?items=172.217.23.206 (I have tried with other ips too)
- Run tests: python3 -m unittest test_app.py (mac setup requirements)


