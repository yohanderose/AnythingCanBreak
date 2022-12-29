package main

import (
	// "fmt"
	// "os/exec"
	"testing"
	"time"
)

func TestGetArtistFromTimeOfDay1(t *testing.T) {
	// 10:00, 12:00, 14:00, 16:00, 18:00
	times := []time.Time{
		time.Date(2018, 1, 1, 10, 0, 0, 0, time.UTC),
		time.Date(2018, 1, 1, 12, 0, 0, 0, time.UTC),
		time.Date(2018, 1, 1, 14, 0, 0, 0, time.UTC),
		time.Date(2018, 1, 1, 16, 0, 0, 0, time.UTC),
		time.Date(2018, 1, 1, 18, 0, 0, 0, time.UTC),
	}

	for _, now := range times {
		artist := getArtistFromTimeOfDay(now)
		if artist != "1" {
			t.Errorf("Expected 1, got %s", artist)
		}
	}
}

func TestGetArtistFromTimeOfDay2(t *testing.T) {
	// 10:30, 12:30, 14:30, 16:30, 18:30
	times := []time.Time{
		time.Date(2018, 1, 1, 10, 30, 0, 0, time.UTC),
		time.Date(2018, 1, 1, 12, 30, 0, 0, time.UTC),
		time.Date(2018, 1, 1, 14, 30, 0, 0, time.UTC),
		time.Date(2018, 1, 1, 16, 30, 0, 0, time.UTC),
		time.Date(2018, 1, 1, 18, 30, 0, 0, time.UTC),
	}

	for _, now := range times {
		artist := getArtistFromTimeOfDay(now)
		if artist != "2" {
			t.Errorf("Expected 2, got %s", artist)
		}
	}
}

func TestGetArtistFromTimeOfDay3(t *testing.T) {
	// 11:00, 13:00, 15:00, 17:00, 19:00
	times := []time.Time{
		time.Date(2018, 1, 1, 11, 0, 0, 0, time.UTC),
		time.Date(2018, 1, 1, 13, 0, 0, 0, time.UTC),
		time.Date(2018, 1, 1, 15, 0, 0, 0, time.UTC),
		time.Date(2018, 1, 1, 17, 0, 0, 0, time.UTC),
		time.Date(2018, 1, 1, 19, 0, 0, 0, time.UTC),
	}

	for _, now := range times {
		artist := getArtistFromTimeOfDay(now)
		if artist != "3" {
			t.Errorf("Expected 3, got %s", artist)
		}
	}
}

func TestGetArtistFromTimeOfDay4(t *testing.T) {
	// 11:30, 13:30, 15:30, 17:30, 19:30
	times := []time.Time{
		time.Date(2018, 1, 1, 11, 30, 0, 0, time.UTC),
		time.Date(2018, 1, 1, 13, 30, 0, 0, time.UTC),
		time.Date(2018, 1, 1, 15, 30, 0, 0, time.UTC),
		time.Date(2018, 1, 1, 17, 30, 0, 0, time.UTC),
		time.Date(2018, 1, 1, 19, 30, 0, 0, time.UTC),
	}
	for _, now := range times {
		artist := getArtistFromTimeOfDay(now)
		if artist != "4" {
			t.Errorf("Expected 4, got %s", artist)
		}
	}
}

func TestPlayAudio(t *testing.T) {
	testArea := ExhibitArea{id: 1}

	setPersonDetected(&testArea, true)
	time.Sleep(2 * time.Second)
	setPersonDetected(&testArea, false)
}

func TestReplayAudio(t *testing.T) {
	testArea := ExhibitArea{id: 2}

	setPersonDetected(&testArea, true)
	time.Sleep(2 * time.Second)
	setPersonDetected(&testArea, false)
	time.Sleep(1 * time.Second)
	setPersonDetected(&testArea, true)
	time.Sleep(2 * time.Second)
	setPersonDetected(&testArea, false)
}

func TestConcurrentPlayAudio(t *testing.T) {
	testArea1 := ExhibitArea{id: 1}
	testArea2 := ExhibitArea{id: 2}

	setPersonDetected(&testArea1, true)
	setPersonDetected(&testArea2, true)
	time.Sleep(3 * time.Second)
	setPersonDetected(&testArea1, false)
	setPersonDetected(&testArea2, false)
}
