package main

import (
    "fmt"
    "log"
    "net/http"
    "os"
)

func main() {
    // Cria um arquivo de log
    logFile, err := os.OpenFile("app.log", os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0666)
    if err != nil {
        log.Fatalf("Erro ao criar arquivo de log: %v", err)
    }
    defer logFile.Close()

    // Configura o log para escrever no arquivo e no console
    log.SetOutput(logFile)
    log.SetFlags(log.LstdFlags | log.Lshortfile)

    log.Println("Aplicação iniciada...")

    http.HandleFunc("/api", func(w http.ResponseWriter, r *http.Request) {
        log.Printf("Recebida requisição de %s para %s", r.RemoteAddr, r.URL.Path)
        fmt.Fprintln(w, "It's working")
    })

    log.Println("Ouvindo na porta 5000...")
    if err := http.ListenAndServe(":5000", nil); err != nil {
        log.Fatalf("Erro ao iniciar servidor: %v", err)
    }
}
