package main

import (
	"fmt"
	"github.com/joho/godotenv"
	"net/http"
	"os"
	"testing"
	"time"
)

var PORT = "3000"

func TestHttpReq(t *testing.T) {
	err := godotenv.Load("../.env")
	if err != nil {
		t.Errorf("Error: %s", err)
	}

	HOST_IP := os.Getenv("HOST_IP")

	// detected
	resp, err := http.Get("http://" + HOST_IP + ":" + PORT + "/data?sensorID=1&range=150")
	if err != nil {
		t.Errorf("Error: %s", err)
	}
	if resp.StatusCode != http.StatusOK {
		t.Errorf("Expected %d, got %d", http.StatusOK, resp.StatusCode)
	} else {
		t.Logf("Starting %d ...", 1)
	}

	time.Sleep(2 * time.Second)

	// not detected
	resp, err = http.Get("http://" + HOST_IP + ":" + PORT + "/data?sensorID=1&range=0")
	if err != nil {
		t.Errorf("Error: %s", err)
	}
	if resp.StatusCode != http.StatusOK {
		t.Errorf("Expected %d, got %d", http.StatusOK, resp.StatusCode)
	} else {
		t.Logf("Stopping %d ...", 1)
	}

}

func TestAllSoundsHttpReq(t *testing.T) {
	err := godotenv.Load("../.env")
	if err != nil {
		t.Errorf("Error: %s", err)
	}

	HOST_IP := os.Getenv("HOST_IP")

	for i := 1; i < 17; i++ {
		sensorID := fmt.Sprintf("%d", i)
		// detected
		resp, err := http.Get("http://" + HOST_IP + ":" + PORT + "/data?sensorID=" + sensorID + "&range=150")
		if err != nil {
			t.Errorf("Error: %s", err)
		}
		if resp.StatusCode != http.StatusOK {
			t.Errorf("Expected %d, got %d", http.StatusOK, resp.StatusCode)
		} else {
			t.Logf("Starting %d ...", i)
		}

		time.Sleep(2 * time.Second)

		resp, err = http.Get("http://" + HOST_IP + ":" + PORT + "/data?sensorID=" + sensorID + "&range=0")
		if err != nil {
			t.Errorf("Error: %s", err)
		}
		if resp.StatusCode != http.StatusOK {
			t.Errorf("Expected %d, got %d", http.StatusOK, resp.StatusCode)
		} else {
			t.Logf("Stopping %d ...", i)
		}
	}
}

func TestConcurrentHttpReq(t *testing.T) {
	err := godotenv.Load("../.env")
	if err != nil {
		t.Errorf("Error: %s", err)
	}

	HOST_IP := os.Getenv("HOST_IP")

	for i := 1; i < 17; i++ {
		sensorID := fmt.Sprintf("%d", i)
		// detected
		resp, err := http.Get("http://" + HOST_IP + ":" + PORT + "/data?sensorID=" + sensorID + "&range=150")
		if err != nil {
			t.Errorf("Error: %s", err)
		}
		if resp.StatusCode != http.StatusOK {
			t.Errorf("Expected %d, got %d", http.StatusOK, resp.StatusCode)
		} else {
			t.Logf("Starting %d ...", i)
		}
		time.Sleep(1 * time.Second)
	}

	time.Sleep(2 * time.Second)

	for i := 1; i < 17; i++ {
		sensorID := fmt.Sprintf("%d", i)
		// not detected
		resp, err := http.Get("http://" + HOST_IP + ":" + PORT + "/data?sensorID=" + sensorID + "&range=0")
		if err != nil {
			t.Errorf("Error: %s", err)
		}
		if resp.StatusCode != http.StatusOK {
			t.Errorf("Expected %d, got %d", http.StatusOK, resp.StatusCode)
		} else {
			t.Logf("Stopping %d ...", i)
		}
		time.Sleep(1 * time.Second)
	}

}
