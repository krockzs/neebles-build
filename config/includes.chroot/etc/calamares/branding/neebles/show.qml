import QtQuick 2.0
import Qt.labs.folderlistmodel 2.1
import QtMultimedia
import calamares.slideshow 1.0

Presentation {
    id: presentation
    anchors.fill: parent

    property var remoteSlides: []
    property int remoteIndex: 0
    property bool remoteAvailable: remoteSlides.length > 0
    property bool currentIsVideo: false
    property bool prepareRequested: false
    property int currentSlot: 0
    property int preparedSlot: 0
    property string preparedExtension: ""
    property bool preparationInFlight: false
    property bool advancePending: false

    function setActiveSlot(number) {
        var xhr = new XMLHttpRequest()

        xhr.open(
            "GET",
            "http://127.0.0.1:28765/active/" + number
        )

        xhr.send()
    }

    function requestNextPreparation() {
        if (presentation.preparationInFlight)
            return

        presentation.preparationInFlight = true

        var xhr = new XMLHttpRequest()

        xhr.open(
            "GET",
            "http://127.0.0.1:28765/prepare"
        )

        xhr.onreadystatechange = function() {
            if (xhr.readyState !== XMLHttpRequest.DONE)
                return

            presentation.preparationInFlight = false

            if (xhr.status !== 200)
                return

            try {
                var result = JSON.parse(xhr.responseText)

                if (result.prepared) {
                    presentation.preparedSlot = result.slot
                    presentation.preparedExtension = result.extension
                }

                if (presentation.advancePending &&
                    presentation.preparedSlot > 0 &&
                    presentation.preparedExtension.length > 0) {
                    presentation.advancePending = false
                    presentation.advance()
                }
            } catch (e) {
            }
        }

        xhr.send()
    }

    Rectangle {
        anchors.fill: parent
        color: "#000000"
        z: -100
    }

    FolderListModel {
        id: remoteFiles
        folder: "file:///run/neebles/calamares/slides"
        nameFilters: [ "*.png", "*.jpg", "*.jpeg", "*.mp4" ]
        showDirs: false
        showFiles: true
    }

    function refreshRemoteSlides() {
        var files = []

        for (var i = 0; i < remoteFiles.count; ++i) {
            var name = remoteFiles.get(i, "fileName")
            var match = name.match(/^([0-9]+)\.(png|jpg|jpeg|mp4)$/i)

            if (match) {
                files.push({
                    number: parseInt(match[1]),
                    name: name,
                    type: match[2].toLowerCase() === "mp4" ? "video" : "image"
                })
            }
        }

        files.sort(function(a, b) {
            return a.number - b.number
        })

        remoteSlides = files

        if (remoteIndex >= remoteSlides.length)
            remoteIndex = 0

        if (remoteSlides.length > 0 && !currentMediaValid())
            showCurrent()
    }

    function currentMediaValid() {
        if (remoteSlides.length === 0)
            return false

        if (remoteIndex < 0 || remoteIndex >= remoteSlides.length)
            return false

        if (currentIsVideo)
            return mediaPlayer.source.toString().length > 0

        return remoteImage.source.toString().length > 0
    }

    function showCurrent() {
        if (remoteSlides.length === 0)
            return

        var item = remoteSlides[remoteIndex]
        var source =
            "file:///run/neebles/calamares/slides/" + item.name

        currentSlot = item.number
        setActiveSlot(currentSlot)

        prepareRequested = false
        imageTimer.stop()
        imagePrepareTimer.stop()
        mediaPlayer.stop()
        mediaPlayer.source = ""
        remoteImage.source = ""

        currentIsVideo = item.type === "video"

        if (currentIsVideo) {
            mediaPlayer.source = source
            mediaPlayer.play()
        } else {
            remoteImage.source = source
            imagePrepareTimer.restart()
            imageTimer.restart()
        }
    }

    function advance() {
        if (presentation.preparedSlot <= 0 ||
            presentation.preparedExtension.length === 0) {
            if (presentation.preparationInFlight) {
                presentation.advancePending = true
            }
            return
        }

        presentation.advancePending = false

        var slot = presentation.preparedSlot
        var extension = presentation.preparedExtension

        presentation.preparedSlot = 0
        presentation.preparedExtension = ""

        var nextIndex = -1

        for (var i = 0; i < remoteSlides.length; ++i) {
            if (remoteSlides[i].number === slot) {
                nextIndex = i
                break
            }
        }

        if (nextIndex < 0) {
            remoteSlides.push({
                number: slot,
                name: slot + "." + extension,
                type: extension === "mp4" ? "video" : "image"
            })

            remoteSlides.sort(function(a, b) {
                return a.number - b.number
            })

            for (var j = 0; j < remoteSlides.length; ++j) {
                if (remoteSlides[j].number === slot) {
                    nextIndex = j
                    break
                }
            }
        }

        if (nextIndex < 0)
            return

        remoteIndex = nextIndex
        showCurrent()
    }

    Timer {
        id: directoryTimer
        interval: 1000
        running: true
        repeat: true
        onTriggered: presentation.refreshRemoteSlides()
    }

    Timer {
        id: imageTimer
        interval: 20000
        repeat: false
        onTriggered: presentation.advance()
    }

    Timer {
        id: imagePrepareTimer
        interval: 18000
        repeat: false

        onTriggered: {
            if (!presentation.currentIsVideo &&
                !presentation.prepareRequested) {
                presentation.prepareRequested = true
                presentation.requestNextPreparation()
            }
        }
    }

    Timer {
        id: videoPositionTimer
        interval: 250
        running: presentation.currentIsVideo &&
                 mediaPlayer.playbackState === MediaPlayer.PlayingState
        repeat: true

        onTriggered: {
            if (!presentation.prepareRequested &&
                mediaPlayer.duration > 0 &&
                mediaPlayer.position >= mediaPlayer.duration - 2000) {
                presentation.prepareRequested = true
                presentation.requestNextPreparation()
            }
        }
    }

    MediaPlayer {
        id: mediaPlayer
        videoOutput: videoOutput
        audioOutput: null

        onMediaStatusChanged: {
            if (mediaStatus === MediaPlayer.EndOfMedia)
                presentation.advance()
        }

        onErrorOccurred: {
            presentation.advance()
        }
    }

    Slide {
        Image {
            id: fallbackImage
            source: "slide1.png"
            width: 467
            height: 280
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.verticalCenter: parent.verticalCenter
            fillMode: Image.PreserveAspectFit
            visible: !presentation.remoteAvailable
        }

        Text {
            anchors.top: fallbackImage.bottom
            anchors.topMargin: 15
            anchors.horizontalCenter: parent.horizontalCenter
            visible: !presentation.remoteAvailable
            text: "Welcome to N.E.E.B.L.E.S. OS.<br/>The installation should complete in a few minutes."
            color: "#ffffff"
            horizontalAlignment: Text.AlignHCenter
        }

        Image {
            id: remoteImage
            anchors.fill: parent
            anchors.margins: 10
            fillMode: Image.PreserveAspectFit
            visible: presentation.remoteAvailable &&
                     !presentation.currentIsVideo
            cache: false
        }

        VideoOutput {
            id: videoOutput
            anchors.fill: parent
            anchors.margins: 10
            visible: presentation.remoteAvailable &&
                     presentation.currentIsVideo
            fillMode: VideoOutput.PreserveAspectFit
        }
    }
}
