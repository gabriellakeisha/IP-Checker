# IPChecker - Bad IP Checker (Ruby)
ruby microservice to check if IPv4 addresses are in the bad IP list.

### install dependencies:
```bash
bundle install
```

### run application:
```bash
ruby src/app.rb
```

### run tests:
```bash
ruby src/app_test.rb
```

### docker:
```bash
docker build -t ipchecker-badips .
docker run -p 8080:80 ipchecker-badips
# Access at: http://localhost:8080/?items=100.200.300.400
```