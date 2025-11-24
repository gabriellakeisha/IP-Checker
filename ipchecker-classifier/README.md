# IPChecker - IPv4/IPv6 Classifier
node.js microservice to classify IP addresses as IPv4 or IPv6.

## Features
- classifies IPv4 addresses (4 groups separated by dots)
- classifies IPv6 addresses (2-8 groups separated by colons)
- returns counts for each type
- comprehensive unit tests with Mocha and Chai
- CI/CD pipeline with GitLab

## API Endpoint
### GET /
classifies IP addresses and returns counts.

