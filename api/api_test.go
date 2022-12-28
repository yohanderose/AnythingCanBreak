package main


import (
	"net/http"
	"github.com/joho/godotenv"
	"testing"
	"os"
	"time"
)

func TestHttpReq(t *testing.T) {
	err := godotenv.Load("../.env")
	if err != nil {
		t.Errorf("Error: %s", err)
	}

	HOST_IP := os.Getenv("HOST_IP")


	// detected
	resp, err := http.Get("http://" + HOST_IP + ":5050/data?sensorID=1&range=150")
	if err != nil {
		t.Errorf("Error: %s", err)
	}
	if resp.StatusCode != http.StatusOK {
		t.Errorf("Expected %d, got %d", http.StatusOK, resp.StatusCode)
	}

	time.Sleep(2 * time.Second)

	// not detected
	resp, err = http.Get("http://" + HOST_IP + ":5050/data?sensorID=1&range=0")
	if err != nil {
		t.Errorf("Error: %s", err)
	}
	if resp.StatusCode != http.StatusOK {
		t.Errorf("Expected %d, got %d", http.StatusOK, resp.StatusCode)
	}

}


