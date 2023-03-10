package main

import (
	"fmt"
	"io/ioutil"
	"net/http"
	"os"
	"os/exec"
	"regexp"
	"sort"
	"strconv"
	"sync"
	"time"

	"github.com/joho/godotenv"

	"fyne.io/fyne/v2"

	"fyne.io/fyne/v2/app"
	"fyne.io/fyne/v2/container"
	"fyne.io/fyne/v2/data/binding"
	"fyne.io/fyne/v2/widget"
	// "strings"
)

var SOUNDS_DIR = "sound"
var APPROX_CEIL_HEIGHT = 240
var areaMap = loadExhibitAreas()
var wg sync.WaitGroup = sync.WaitGroup{}
var CALBRATION_SECONDS = 5
var startTime = time.Now()
var ffmpegLog = getFfmpegLog()

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

	for h := 11; h < 21; h += 2 {
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

func getFfmpegLog() *os.File {
	f, err := os.OpenFile("/tmp/go_ffmpeg", os.O_APPEND|os.O_WRONLY|os.O_CREATE, 0600)
	if err != nil {
		panic(err)
	}
	return f
}

type ExhibitArea struct {
	id                      int
	personDetected          bool
	bindPersonDetected      binding.String
	proc                    exec.Cmd
	triggerRange            int
	_floorRanges            []int
	floorRange              int
	calibrationStarted      bool
	calibrationFinished     bool
	bindCalibrationFinished binding.String
	startTime               time.Time
}

func calibrateRange(exhibitArea *ExhibitArea, val int) {
	exhibitArea._floorRanges = (append(exhibitArea._floorRanges, val))
	sort.Ints(exhibitArea._floorRanges)
	exhibitArea.floorRange = exhibitArea._floorRanges[len(exhibitArea._floorRanges)/2]
	exhibitArea.triggerRange = exhibitArea.floorRange - 20
}

func setPersonDetected(exhibitArea *ExhibitArea, personDetected bool) {
	exhibitArea.personDetected = personDetected
	exhibitArea.bindPersonDetected.Set("Person detected: " + strconv.FormatBool(exhibitArea.personDetected))
	if !exhibitArea.personDetected {
		stopAudio(exhibitArea)
	} else {
		wg.Add(1)
		go playAudio(exhibitArea)
	}
}

func playAudio(exhibitArea *ExhibitArea) {
	defer wg.Done()
	for {
		if !exhibitArea.personDetected {
			break
		}
		artist := getArtistFromTimeOfDay(time.Now())
		// artist := "4"
		channel := exhibitArea.id - 1
		chanelString := fmt.Sprintf("%d", channel)
		audioFile := playlist[artist][channel]
		outputDevice := "1"

		cmdString := ""

		if artist != "4" {
			cmdString = `ffmpeg -i ` + audioFile + ` -ac 16 -filter_complex "[0:a]loudnorm=I=-14:LRA=5:TP=-1.5[a];[a]pan=stereo|c` + chanelString + `=c0[b];[b]volume=1.6[c]" -map "[c]" -f audiotoolbox -audio_device_index ` + outputDevice + ` -`
		} else {
			cmdString = `ffmpeg -i ` + audioFile + ` -ac 16 -filter_complex "[0:a]loudnorm=I=-14:LRA=5:TP=-1.5[a];[a]pan=stereo|c` + chanelString + `=c0[b];[b]volume=1.4[c]" -map "[c]" -f audiotoolbox -audio_device_index ` + outputDevice + ` -`
		}

		// cmdString = `ffmpeg -i ` + audioFile + ` -ac 2 -filter_complex "[0:a]loudnorm=I=-16:LRA=5:TP=-1.5[a];[a]pan=stereo|c` + chanelString + `=c0[b]" -map "[b]" -f alsa default`
		// fmt.Println(cmdString)
		// write to log

		ffmpegLog.WriteString(time.Now().String() + " | " + cmdString + "\n")

		exhibitArea.proc = *exec.Command("sh", "-c", cmdString)

		exhibitArea.proc.Start()
		exhibitArea.proc.Wait()
	}
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

	ffmpegLog.WriteString(time.Now().String() + " | " + "Killed " + strconv.Itoa(exhibitArea.id) + "\n")

	// Reset to original volume
	// cmdString = `ffmpeg -f lavfi -i anullsrc=channel_layout=stereo:sample_rate=44100 -filter_complex "[0:a]volume=1[a];[a]pan=stereo|c` + chanelString + `=c0[b]" -map "[b]" -f alsa hw:` + outputDevice + `,0`
	// resetVolume := *exec.Command("sh", "-c", cmdString)
	// resetVolume.Start()
	// resetVolume.Wait()
}

func processRequest(areaId_ int, range_ int) int {
	area, ok := areaMap[areaId_]

	if !ok {
		return 1
	} else {
		if !area.calibrationStarted {
			area.calibrationStarted = true
			area.startTime = time.Now()
		}
		if area.calibrationFinished {
			if area.personDetected == false && range_ > 0 && range_ <= area.triggerRange {
				setPersonDetected(area, true)
			} else if area.personDetected == true && range_ == area.floorRange {
				setPersonDetected(area, false)
			}
		} else {
			if range_ > 0 {
				calibrateRange(area, range_)
			}
			if area.calibrationStarted && (time.Now().After(startTime.Add(time.Duration(CALBRATION_SECONDS)))) {
				area.calibrationFinished = true
				area.bindCalibrationFinished.Set("Calibrated: " + strconv.FormatBool(area.personDetected))
			}

		}
		return 0
	}
}

func serveAPI() {
	HOST_IP := os.Getenv("HOST_IP")
	fmt.Println("HOST_IP: " + HOST_IP)

	http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		fmt.Fprintf(w, "Welcome to new server again!")
	})

	http.HandleFunc("/data", func(w http.ResponseWriter, r *http.Request) {
		areaId_, _ := strconv.Atoi(r.URL.Query().Get("sensorID"))
		range_, _ := strconv.Atoi(r.URL.Query().Get("range"))
		// motion_, _ := strconv.Atoi(r.URL.Query().Get("motion"))

		err := processRequest(areaId_, range_)
		if err == 0 {
			fmt.Fprintf(w, "OK")
		} else {
			fmt.Fprintf(w, "ERROR")
		}

		return
	})

	for i := 1; i <= 16; i++ {
		areaId_ := i
		http.HandleFunc("/"+strconv.Itoa(i), func(w http.ResponseWriter, r *http.Request) {
			range_, _ := strconv.Atoi(r.URL.Query().Get("range"))
			// motion_, _ := strconv.Atoi(r.URL.Query().Get("motion"))

			err := processRequest(areaId_, range_)
			if err == 0 {
				fmt.Fprintf(w, "OK")
			} else {
				fmt.Fprintf(w, "ERROR")
			}

			return
		})
	}

	http.ListenAndServe(HOST_IP+":5000", nil)
}

func runGUI() {
	a := app.New()
	w := a.NewWindow("ASM")

	// Create fyne grid of areas with bindings to floor range, trigger range and personDetected
	var areaBoxes [16]fyne.CanvasObject
	for i := 1; i <= 16; i++ {
		area, ok := areaMap[i]
		if !ok {
			fmt.Println("Area not found")
		} else {
			area.bindCalibrationFinished.Set("Calibrated: " + strconv.FormatBool(area.personDetected))
			area.bindPersonDetected.Set("Person detected: " + strconv.FormatBool(area.personDetected))
			title := widget.NewLabel("Area " + strconv.Itoa(area.id))
			title.TextStyle = fyne.TextStyle{Bold: true}
			calibrated := widget.NewLabelWithData(area.bindCalibrationFinished)
			detected := widget.NewLabelWithData(area.bindPersonDetected)

			// intro.Wrapping = fyne.TextWrapWord

			content := container.NewMax()

			areaBoxes[i-1] = container.NewBorder(
				container.NewVBox(
					title,
					widget.NewSeparator(),
					calibrated,
					detected,
				), nil, nil, nil, content)
		}
	}

	grid := container.NewGridWithColumns(4, areaBoxes[0], areaBoxes[1], areaBoxes[2], areaBoxes[3], areaBoxes[4], areaBoxes[5], areaBoxes[6], areaBoxes[7], areaBoxes[8], areaBoxes[9], areaBoxes[10], areaBoxes[11], areaBoxes[12], areaBoxes[13], areaBoxes[14], areaBoxes[15])

	hello := widget.NewLabel("AnythingCanBreak System Monitor")
	w.SetContent(container.NewVBox(
		hello,
		grid,
		// widget.NewButton("Hi!", func() {
		// 	hello.SetText("Welcome :)")
		// }),
	))

	w.ShowAndRun()
}

func loadExhibitAreas() map[int]*ExhibitArea {
	// load exhibit areas from file
	// for now, just hard code
	areaMap_ := map[int]*ExhibitArea{}

	for i := 1; i < 17; i++ {
		areaMap_[i] = &ExhibitArea{
			id:                      i,
			personDetected:          false,
			bindPersonDetected:      binding.NewString(),
			calibrationStarted:      false,
			calibrationFinished:     false,
			bindCalibrationFinished: binding.NewString(),
			startTime:               time.Now(),
		}
		calibrateRange(areaMap_[i], APPROX_CEIL_HEIGHT)
	}
	return areaMap_
}

func main() {
	// Load .env file
	err := godotenv.Load("../.env")
	if err != nil {
		panic(err)
	}

	go serveAPI()
	runGUI()

	// setPersonDetected(areaMap[1], true)
	// time.Sleep(3 * time.Second)
	// setPersonDetected(areaMap[1], false)

	wg.Wait()
}
