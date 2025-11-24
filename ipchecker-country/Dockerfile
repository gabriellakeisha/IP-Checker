# Bbuild stage
FROM golang:1.23-alpine AS builder

WORKDIR /app

# copy go mod files first (for caching)
COPY go.mod go.sum* ./

# download dependencies
RUN go mod download

# copy source code from src directory
COPY src/ ./

# build the application
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o main .

# final stage
FROM alpine:latest

RUN apk --no-cache add ca-certificates

WORKDIR /root/

# copy the binary from builder
COPY --from=builder /app/main .

# expose port 80
EXPOSE 80

# run the binary
CMD ["./main"]