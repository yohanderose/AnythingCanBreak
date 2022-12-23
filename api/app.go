package main

import (
	"fmt"
	// "io/ioutil"
	// "log"
	"os/exec"
	"strings"
	"time"
	// "net/http"
)

var SOUNDS_DIR = "sound"

func getPlaylist() map[string][]string {
	playlists := make(map[string][]string)

	// walk through the artists

	for i := 1; i < 5; i++ {
		artist := fmt.Sprintf("%d", i)

		for j := 0; j < 16; j++ {
			trackFile := SOUNDS_DIR + "/" + artist + "/speaker" + fmt.Sprintf("%d", j+1) + ".wav"
			playlists[artist] = append(playlists[artist], trackFile)
		}

	}

	// for _, a := range artist_dirs {
	// 	// walk through songs
	// 	songs, err := ioutil.ReadDir(SOUNDS_DIR + "/" + a.Name())
	// 	if err != nil {
	// 		log.Fatal(err)
	// 	}
	// 	for _, s := range songs {
	// 		// add to playlist
	// 		playlists[a.Name()] = append(playlists[a.Name()], s.Name())
	// 	}
	// 	break
	// }
	return playlists
}

var playlist = getPlaylist()

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

	go func() {
		if personDetected {
			go playAudio(exhibitArea)
		} else {
			exhibitArea.proc.Process.Kill()
		}

	}()
}

func playAudio(exhibitArea *ExhibitArea) {
	artist := getArtistFromTimeofDay(time.Now())
	channel := exhibitArea.id - 1
	chanelString := fmt.Sprintf("%d", channel)
	audioFile := playlist[artist][channel]
	outputDevice := "1"

	cmdString := `ffmpeg -i ` + audioFile + ` -ac 2 -filter_complex "[0:a]pan=stereo|c` + chanelString + `=c0[a];[a]dynaudnorm=p=0.9:s=5[a_norm]" -map "[a_norm]" -f alsa hw:` + outputDevice + `,0 -loglevel quiet &
	`

	fmt.Println(cmdString)
	cmd := strings.Split(cmdString, " ")
	exhibitArea.proc = *exec.Command(cmd[0], cmd[1:]...)

	exhibitArea.proc.Start()
}

func stopAudio(exhibitArea *ExhibitArea) {
	exhibitArea.proc.Process.Kill()
}

var areaMap = map[int]*ExhibitArea{}

func main() {
	// http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
	// 	fmt.Fprintf(w, "Welcome to new server again!")
	// })

	for i := 1; i < 17; i++ {
		areaMap[i] = &ExhibitArea{id: i}
	}

	setPersonDetected(areaMap[1], true)
	time.Sleep(5 * time.Second)
	setPersonDetected(areaMap[1], false)

}
