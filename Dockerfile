# Etapa de build
FROM golang:1.19 as builder
WORKDIR /app
COPY app/go.mod app/go.sum ./
RUN go mod download
COPY app/*.go ./
RUN go mod tidy
RUN ls -la /app
RUN go env
RUN CGO_ENABLED=0 GOOS=linux go build -o /main .

# Etapa final
FROM alpine:latest
WORKDIR /
COPY --from=builder /main .
CMD ["./main"]
