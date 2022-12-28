package main

import (
	"github.com/joho/godotenv"
	"net/http"
	"os"
	"testing"
	"time"
)

var testMap = map[int]*ExhibitArea{}

// func TestCreateExhibitArea(t *testing.T) {

// 	mapping := make(map[int]ExhibitArea)
// 	for i := 0; i < 10; i++ {
// 		mapping[i] = ExhibitArea{id: i}

// 		if mapping[i].id != i {
// 			t.Errorf("Expected %d, got %d", i, mapping[i].id)
// 		}

// 		// destroy the exhibit area
// 	}
// }

// func TestSetPersonDetected(t *testing.T) {

// 	e := ExhibitArea{id: 1}

// 	setPersonDetected(&e, true)

// 	if e.personDetected != true {
// 		t.Errorf("Expected %v, got %v", true, e.personDetected)
// 	}

// 	time.Sleep(1 * time.Second)

// 	setPersonDetected(&e, false)

// 	if e.personDetected != false {
// 		t.Errorf("Expected %v, got %v", false, e.personDetected)
// 	}
// }

func TestHttpReq(t *testing.T) {
	err := godotenv.Load("../.env")
	if err != nil {
		panic(err)
	}

	HOST_IP := os.Getenv("HOST_IP")

	// test http get request detected
	resp, err := http.Get("http://" + HOST_IP + ":5050/data?sensorID=1&range=180")
	if err != nil {
		t.Errorf("Error: %s", err)
	}

	if resp.StatusCode != http.StatusOK {
		t.Errorf("Expected %d, got %d", http.StatusOK, resp.StatusCode)
	}

	time.Sleep(2 * time.Second)

	// test http get request not detected
	resp, err = http.Get("http://" + HOST_IP + ":5050/data?sensorID=1&range=0")
	if err != nil {
		t.Errorf("Error: %s", err)
	}

	if resp.StatusCode != http.StatusOK {
		t.Errorf("Expected %d, got %d", http.StatusOK, resp.StatusCode)
	}

}
