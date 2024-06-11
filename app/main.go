package main

import (
    "context"
    "encoding/json"
    "fmt"
    "net/http"
    "os"

    "k8s.io/client-go/kubernetes"
    "k8s.io/client-go/rest"
    "k8s.io/client-go/tools/clientcmd"
    metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
)

func main() {
    var config *rest.Config
    var err error

    kubeconfig := os.Getenv("KUBECONFIG")
    if kubeconfig != "" {
        config, err = clientcmd.BuildConfigFromFlags("", kubeconfig)
    } else {
        config, err = rest.InClusterConfig()
    }
    if err != nil {
        panic(err.Error())
    }

    clientset, err := kubernetes.NewForConfig(config)
    if err != nil {
        panic(err.Error())
    }

    http.HandleFunc("/clusters", func(w http.ResponseWriter, r *http.Request) {
        clusterInfo := map[string]string{
            "cluster_name": "MeuCluster",
        }
        json.NewEncoder(w).Encode(clusterInfo)
    })

    http.HandleFunc("/nodes", func(w http.ResponseWriter, r *http.Request) {
        nodes, err := clientset.CoreV1().Nodes().List(context.TODO(), metav1.ListOptions{})
        if err != nil {
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
        if r.Method == http.MethodPost {
            var ns struct {
                Name string `json:"name"`
            }
            err := json.NewDecoder(r.Body).Decode(&ns)
            if err != nil || ns.Name == "" {
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
                http.Error(w, err.Error(), http.StatusInternalServerError)
                return
            }
            fmt.Fprintf(w, "Namespace %s created successfully", ns.Name)
        } else {
            namespaces, err := clientset.CoreV1().Namespaces().List(context.TODO(), metav1.ListOptions{})
            if err != nil {
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

    http.ListenAndServe(":5000", nil)
}
