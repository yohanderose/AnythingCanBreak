package main

import (
	"fmt"
	"github.com/joho/godotenv"
	"io/ioutil"
	"net/http"
	"os"
	"os/exec"
	"regexp"
	"strconv"
	"sync"
	"time"
	// "strings"
)

var SOUNDS_DIR = "sound"
var APPROX_CEIL_HEIGHT = 240
var areaMap = loadExhibitAreas()
var wg sync.WaitGroup = sync.WaitGroup{}

func getPlaylist() map[string][]string {
	playlists := make(map[string][]string)

	// walk through the artists

	for i := 1; i < 5; i++ {
		artist := fmt.Sprintf("%d", i)
		files, err := ioutil.ReadDir(SOUNDS_DIR + "/" + artist)
		if err != nil {
			fmt.Println(err)

		}

		re := regexp.MustCompile(`\.(mp3|wav|ogg|aif)$`)
		ext := re.FindAllString(files[0].Name(), -1)

		for j := 0; j < 16; j++ {
			trackFile := SOUNDS_DIR + "/" + artist + "/speaker" + fmt.Sprintf("%d", j+1) + ext[0]
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

func getArtistFromTimeOfDay(now time.Time) string {

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
	triggerRange   int
}

func setPersonDetected(exhibitArea *ExhibitArea, personDetected bool) {
	exhibitArea.personDetected = personDetected

	func() {
		if personDetected {
			go playAudio(exhibitArea)
		} else {
			stopAudio(exhibitArea)
		}
	}()
}

func playAudio(exhibitArea *ExhibitArea) {
	artist := getArtistFromTimeOfDay(time.Now())
	channel := exhibitArea.id - 1
	chanelString := fmt.Sprintf("%d", channel)
	audioFile := playlist[artist][channel]
	outputDevice := "1"

	// cmdString := `ffmpeg -i ` + audioFile + ` -ac 2 -filter_complex "[0:a]loudnorm=I=-16:LRA=5:TP=-1.5[a];[a]pan=stereo|c` + chanelString + `=c0[b]" -map "[b]" -f alsa hw:` + outputDevice + `,0`

	cmdString := ""
	if (artist != "4") {
		cmdString = `ffmpeg -i ` + audioFile + ` -ac 16 -filter_complex "[0:a]loudnorm=I=-14:LRA=5:TP=-1.5[a];[a]pan=stereo|c` + chanelString + `=c0[b];[b]volume=1.4[c]" -map "[c]" -f audiotoolbox -audio_device_index ` + outputDevice + ` -`
	} else {
		cmdString = `ffmpeg -i ` + audioFile + ` -ac 16 -filter_complex "[0:a]loudnorm=I=-14:LRA=5:TP=-1.5[a];[a]pan=stereo|c` + chanelString + `=c0[b];[b]volume=1.2[c]" -map "[c]" -f audiotoolbox -audio_device_index ` + outputDevice + ` -`
	}

	exhibitArea.proc = *exec.Command("sh", "-c", cmdString)

	wg.Add(1)
	exhibitArea.proc.Start()
}

func stopAudio(exhibitArea *ExhibitArea) {
	// outputDevice := "1"
	// chanelString := fmt.Sprintf("%d", exhibitArea.id-1)

	// Fade out audio
	// cmdString := `ffmpeg -f lavfi -i anullsrc=channel_layout=stereo:sample_rate=44100 -t 1 -filter_complex "[0:a]afade=t=out:st=0:d=1[a];[a]pan=stereo|c` + chanelString + `=c0[b]" -map "[b]" -f alsa hw:` + outputDevice + `,0`

	// fadeOut := *exec.Command("sh", "-c", cmdString)
	// fadeOut.Start()
	// fadeOut.Wait()

	exhibitArea.proc.Process.Kill()
	exhibitArea.proc.Wait()

	// Reset to original volume
	// cmdString = `ffmpeg -f lavfi -i anullsrc=channel_layout=stereo:sample_rate=44100 -filter_complex "[0:a]volume=1[a];[a]pan=stereo|c` + chanelString + `=c0[b]" -map "[b]" -f alsa hw:` + outputDevice + `,0`
	// resetVolume := *exec.Command("sh", "-c", cmdString)
	// resetVolume.Start()
	// resetVolume.Wait()
	wg.Done()
}

func serveAPI() {
	HOST_IP := os.Getenv("HOST_IP")
	fmt.Println("HOST_IP: " + HOST_IP)

	http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		fmt.Fprintf(w, "Welcome to new server again!")
	})

	// get request with area id
	http.HandleFunc("/data", func(w http.ResponseWriter, r *http.Request) {
		areaId_, _ := strconv.Atoi(r.URL.Query().Get("sensorID"))
		range_, _ := strconv.Atoi(r.URL.Query().Get("range"))
		// motion_, _ := strconv.Atoi(r.URL.Query().Get("motion"))

		area, ok := areaMap[areaId_]
		if !ok {
			fmt.Fprintf(w, "Area not found")
		} else {
			if area.personDetected == false && range_ > 0 && range_ <= area.triggerRange {
				setPersonDetected(area, true)
			} else {
				setPersonDetected(area, false)
			}
			w.WriteHeader(http.StatusOK)
			fmt.Fprintf(w, `{"sensorID": %d, "range": %d}`, areaId_, range_)
			return
		}

		return

	})

	http.ListenAndServe(HOST_IP+":5050", nil)
}

func loadExhibitAreas() map[int]*ExhibitArea {
	// load exhibit areas from file
	// for now, just hard code
	areaMap_ := map[int]*ExhibitArea{}

	for i := 1; i < 17; i++ {
		areaMap_[i] = &ExhibitArea{
			id:             i,
			personDetected: false,
			triggerRange:   APPROX_CEIL_HEIGHT,
		}
	}
	return areaMap_
}

func main() {
	// Load .env file
	err := godotenv.Load("../.env")
	if err != nil {
		panic(err)
	}

	serveAPI()

	// setPersonDetected(areaMap[1], true)
	// time.Sleep(2 * time.Second)
	// setPersonDetected(areaMap[1], false)

}
