package main

import (
    "context"
    "encoding/json"
    "fmt"
    "log"
    "net/http"
    "os"

    "k8s.io/client-go/kubernetes"
    "k8s.io/client-go/rest"
    "k8s.io/client-go/tools/clientcmd"
    metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
    "k8s.io/api/core/v1"
)

func main() {
    log.Println("Starting application...")

    var config *rest.Config
    var err error

    kubeconfig := os.Getenv("KUBECONFIG")
    if kubeconfig != "" {
        log.Printf("Using kubeconfig from %s", kubeconfig)
        config, err = clientcmd.BuildConfigFromFlags("", kubeconfig)
    } else {
        log.Println("Using in-cluster kubeconfig")
        config, err = rest.InClusterConfig()
    }
    if err != nil {
        log.Fatalf("Error building kubeconfig: %v", err)
    }

    clientset, err := kubernetes.NewForConfig(config)
    if err != nil {
        log.Fatalf("Error creating Kubernetes client: %v", err)
    }

    // Adicionando rota /api
    http.HandleFunc("/api", func(w http.ResponseWriter, r *http.Request) {
        log.Printf("Received request for /api from %s", r.RemoteAddr)
        w.WriteHeader(http.StatusOK)
        fmt.Fprintln(w, "API is working")
    })

    http.HandleFunc("/clusters", func(w http.ResponseWriter, r *http.Request) {
        log.Printf("Received request for /clusters from %s", r.RemoteAddr)
        clusterInfo := map[string]string{
            "cluster_name": "MeuCluster",
        }
        json.NewEncoder(w).Encode(clusterInfo)
    })

    http.HandleFunc("/nodes", func(w http.ResponseWriter, r *http.Request) {
        log.Printf("Received request for /nodes from %s", r.RemoteAddr)
        nodes, err := clientset.CoreV1().Nodes().List(context.TODO(), metav1.ListOptions{})
        if err != nil {
            log.Printf("Error listing nodes: %v", err)
            http.Error(w, err.Error(), http.StatusInternalServerError)
            return
        }
        nodeNames := make([]string, len(nodes.Items))
        for i, node := range nodes.Items {
            nodeNames[i] = node.Name
        }
        json.NewEncoder(w).Encode(nodeNames)
    })

    http.HandleFunc("/namespaces", func(w http.ResponseWriter, r *http.Request) {
        log.Printf("Received request for /namespaces from %s", r.RemoteAddr)
        if r.Method == http.MethodPost {
            var ns struct {
                Name string `json:"name"`
            }
            err := json.NewDecoder(r.Body).Decode(&ns)
            if err != nil || ns.Name == "" {
                log.Printf("Invalid namespace name: %v", err)
                http.Error(w, "Invalid namespace name", http.StatusBadRequest)
                return
            }
            namespace := &v1.Namespace{
                ObjectMeta: metav1.ObjectMeta{
                    Name: ns.Name,
                },
            }
            _, err = clientset.CoreV1().Namespaces().Create(context.TODO(), namespace, metav1.CreateOptions{})
            if err != nil {
                log.Printf("Error creating namespace: %v", err)
                http.Error(w, err.Error(), http.StatusInternalServerError)
                return
            }
            log.Printf("Namespace %s created successfully", ns.Name)
            fmt.Fprintf(w, "Namespace %s created successfully", ns.Name)
        } else {
            namespaces, err := clientset.CoreV1().Namespaces().List(context.TODO(), metav1.ListOptions{})
            if err != nil {
                log.Printf("Error listing namespaces: %v", err)
                http.Error(w, err.Error(), http.StatusInternalServerError)
                return
            }
            namespaceNames := make([]string, len(namespaces.Items))
            for i, ns := range namespaces.Items {
                namespaceNames[i] = ns.Name
            }
            json.NewEncoder(w).Encode(namespaceNames)
        }
    })

    log.Println("Starting server on :5000")
    log.Fatal(http.ListenAndServe(":5000", nil))
}
