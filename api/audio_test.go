package main

import (
	// "fmt"
	// "os/exec"
	"testing"
	"time"
)

func TestGetArtistFromTimeOfDay(t *testing.T) {
	// 10:00
	now := time.Date(2018, 1, 1, 10, 0, 0, 0, time.UTC)
	artist := getArtistFromTimeOfDay(now)
	if artist != "1" {
		t.Errorf("Expected artist 1, got %s", artist)

	}

}

func TestGetArtistFromTimeOfDay2(t *testing.T) {
	// 10:30
	now := time.Date(2018, 1, 1, 10, 30, 0, 0, time.UTC)
	artist := getArtistFromTimeOfDay(now)
	if artist != "2" {
		t.Errorf("Expected artist 2, got %s", artist)

	}

}

func TestGetArtistFromTimeOfDay3(t *testing.T) {
	// 11:00
	now := time.Date(2018, 1, 1, 11, 0, 0, 0, time.UTC)
	artist := getArtistFromTimeOfDay(now)
	if artist != "3" {
		t.Errorf("Expected artist 3, got %s", artist)

	}

}

func TestGetArtistFromTimeOfDay4(t *testing.T) {
	// 11:30
	now := time.Date(2018, 1, 1, 11, 30, 0, 0, time.UTC)
	artist := getArtistFromTimeOfDay(now)
	if artist != "4" {
		t.Errorf("Expected artist 4, got %s", artist)

	}
}

func TestPlayAudio(t *testing.T) {
	testArea := ExhibitArea{id: 1}

	setPersonDetected(&testArea, true)
	time.Sleep(2 * time.Second)
	setPersonDetected(&testArea, false)
}
