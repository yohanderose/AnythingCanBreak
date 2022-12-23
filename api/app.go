package main

import (
	"fmt"
	"io/ioutil"
	"log"
	"os/exec"
	"strings"
	"time"
	// "net/http"
)

var SOUNDS_DIR = "./sounds"

func getAudioFiles() map[string][]string {
	playlists := make(map[string][]string)

	files, err := ioutil.ReadDir(SOUNDS_DIR)
	if err != nil {
		log.Fatal(err)
	}

	var audioFiles []string
	for _, f := range files {
		audioFiles = append(audioFiles, f.Name())
	}
	return playlists
}

func getArtistFromTimeofDay(now time.Time) string {

	for h := 11; h < 21; h++ {
		switch {
		case now.Hour() < h && now.Minute() < 30:
			return "1"
		case now.Hour() < h && now.Minute() >= 30:
			return "2"
		case now.Hour() < h+1 && now.Minute() < 30:
			return "3"
		case now.Hour() < h+1 && now.Minute() >= 30:
			return "4"
		}
	}
	return "4"
}

type ExhibitArea struct {
	id             int
	personDetected bool
	proc           exec.Cmd
}

func setPersonDetected(exhibitArea *ExhibitArea, personDetected bool) {
	exhibitArea.personDetected = personDetected
	if personDetected {
		playAudio(exhibitArea)
	}
}

func playAudio(exhibitArea *ExhibitArea) {
	channel := exhibitArea.id - 1
	chanelString := fmt.Sprintf("%d", channel)

	cmdString := "./play_sound.sh sounds/SPEAKER1_BIRD_5_#5_v1.wav " + chanelString
	cmd := strings.Split(cmdString, " ")
	exhibitArea.proc = *exec.Command(cmd[0], cmd[1:]...)

	exhibitArea.proc.Start()
	time.Sleep(3 * time.Second)
	exhibitArea.proc.Process.Kill()
}

func stopAudio(exhibitArea *ExhibitArea) {
	exhibitArea.proc.Process.Kill()
}

func main() {
	// http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
	// 	fmt.Fprintf(w, "Welcome to new server again!")
	// })
	area := ExhibitArea{id: 1, personDetected: false}
	// setPersonDetected(&area, true)
	// time.Sleep(3 * time.Second)
	// stopAudio(&area)

	playAudio(&area)
}
