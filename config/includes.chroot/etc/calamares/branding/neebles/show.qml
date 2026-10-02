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
    property int currentSlot: 0

    property string slideHeading: ""
    property string slideBody: ""
    property string slideHighlight: ""

    function setActiveSlot(number) {
        var xhr = new XMLHttpRequest()

        xhr.open(
            "GET",
            "http://127.0.0.1:28765/active/" + number
        )

        xhr.send()
    }

    function clearSlideText() {
        slideHeading = ""
        slideBody = ""
        slideHighlight = ""
    }

    function escapeHtml(value) {
        return value
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
    }

    function richText(value) {
        var result = escapeHtml(value)

        result = result
            .replace(/\[b\]/g, "<b>")
            .replace(/\[\/b\]/g, "</b>")
            .replace(/\[i\]/g, "<i>")
            .replace(/\[\/i\]/g, "</i>")
            .replace(/\[u\]/g, "<u>")
            .replace(/\[\/u\]/g, "</u>")
            .replace(/\r\n/g, "\n")
            .replace(/\r/g, "\n")
            .replace(/\n/g, "<br/>")

        return result
    }

    function extractBlock(content, name) {
        var opening = "[" + name + "]"
        var closing = "[/" + name + "]"

        var start = content.indexOf(opening)

        if (start < 0)
            return ""

        start += opening.length

        var end = content.indexOf(
            closing,
            start
        )

        if (end < 0)
            return ""

        return content
            .substring(start, end)
            .trim()
    }

    function localizedContent(raw) {
        var lines = raw
            .replace(/\r\n/g, "\n")
            .replace(/\r/g, "\n")
            .split("\n")

        var sections = ({})
        var currentLocale = ""

        for (var i = 0; i < lines.length; ++i) {
            var line = lines[i]
            var match = line
                .trim()
                .match(/^\[([A-Za-z]{2,3}(?:_[A-Za-z0-9]+)?)\]$/)

            if (match) {
                currentLocale = match[1]
                    .replace("-", "_")

                sections[currentLocale] = ""
                continue
            }

            if (currentLocale.length > 0) {
                if (sections[currentLocale].length > 0)
                    sections[currentLocale] += "\n"

                sections[currentLocale] += line
            }
        }

        var localeName = Qt.locale().name
            .replace("-", "_")
            .replace(/\.UTF-8$/i, "")
            .replace(/\.utf8$/i, "")

        if (sections[localeName] !== undefined)
            return sections[localeName]

        if (sections["en_US"] !== undefined)
            return sections["en_US"]

        return ""
    }

    function parseSlideText(raw) {
        var content = localizedContent(raw)

        if (content.length === 0) {
            clearSlideText()
            return
        }

        slideHeading = richText(
            extractBlock(
                content,
                "heading"
            )
        )

        slideBody = richText(
            extractBlock(
                content,
                "body"
            )
        )

        slideHighlight = richText(
            extractBlock(
                content,
                "highlight"
            )
        )
    }

    function loadSlideText(number) {
        clearSlideText()

        var requestedSlot = number
        var xhr = new XMLHttpRequest()

        xhr.open(
            "GET",
            "http://127.0.0.1:28765/text/" + number
        )

        xhr.onreadystatechange = function() {
            if (xhr.readyState !== XMLHttpRequest.DONE)
                return

            if (presentation.currentSlot !== requestedSlot)
                return

            if (xhr.status !== 200) {
                presentation.clearSlideText()
                return
            }

            presentation.parseSlideText(
                xhr.responseText
            )
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
        nameFilters: [
            "*.png",
            "*.jpg",
            "*.jpeg",
            "*.mp4"
        ]
        showDirs: false
        showFiles: true
    }

    function indexForSlot(number) {
        for (var i = 0; i < remoteSlides.length; ++i) {
            if (remoteSlides[i].number === number)
                return i
        }

        return -1
    }

    function refreshRemoteSlides() {
        var files = []
        var knownSlots = ({})

        for (var i = 0; i < remoteFiles.count; ++i) {
            var name = remoteFiles.get(
                i,
                "fileName"
            )

            var match = name.match(
                /^([0-9]+)\.(png|jpg|jpeg|mp4)$/i
            )

            if (!match)
                continue

            var number = parseInt(
                match[1]
            )

            if (number < 1 || number > 20)
                continue

            if (knownSlots[number])
                continue

            knownSlots[number] = true

            files.push({
                number: number,
                name: name,
                type:
                    match[2].toLowerCase() === "mp4"
                    ? "video"
                    : "image"
            })
        }

        files.sort(function(a, b) {
            return a.number - b.number
        })

        remoteSlides = files

        if (remoteSlides.length === 0) {
            remoteIndex = 0
            return
        }

        if (currentSlot > 0) {
            var currentIndex =
                indexForSlot(currentSlot)

            if (currentIndex >= 0) {
                remoteIndex = currentIndex
                return
            }
        }

        remoteIndex = 0
        showCurrent()
    }

    function showCurrent() {
        if (remoteSlides.length === 0)
            return

        if (
            remoteIndex < 0 ||
            remoteIndex >= remoteSlides.length
        ) {
            remoteIndex = 0
        }

        var item = remoteSlides[remoteIndex]

        var source =
            "file:///run/neebles/calamares/slides/" +
            item.name

        currentSlot = item.number
        currentIsVideo =
            item.type === "video"

        setActiveSlot(currentSlot)
        loadSlideText(currentSlot)

        imageTimer.stop()
        mediaPlayer.stop()

        mediaPlayer.source = ""
        remoteImage.source = ""

        if (currentIsVideo) {
            mediaPlayer.source = source
            mediaPlayer.play()
        } else {
            remoteImage.source = source
            imageTimer.restart()
        }
    }

    function advanceLocal() {
        if (remoteSlides.length === 0)
            return

        var index =
            indexForSlot(currentSlot)

        if (index < 0)
            index = remoteIndex

        index += 1

        if (index >= remoteSlides.length)
            index = 0

        remoteIndex = index
        showCurrent()
    }

    Timer {
        id: directoryTimer
        interval: 1000
        running: true
        repeat: true

        onTriggered:
            presentation.refreshRemoteSlides()
    }

    Timer {
        id: imageTimer
        interval: 20000
        repeat: false

        onTriggered:
            presentation.advanceLocal()
    }

    MediaPlayer {
        id: mediaPlayer
        videoOutput: videoOutput
        audioOutput: null

        onMediaStatusChanged: {
            if (
                mediaStatus === MediaPlayer.EndOfMedia
            ) {
                presentation.advanceLocal()
            }
        }

        onErrorOccurred: {
            presentation.advanceLocal()
        }
    }

    Slide {
        Item {
            id: leftPanel

            anchors.left: parent.left
            anchors.top: parent.top
            anchors.bottom: parent.bottom

            width: parent.width * 0.25

            Column {
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.verticalCenter:
                    parent.verticalCenter

                anchors.leftMargin: 18
                anchors.rightMargin: 18

                spacing: 14

                Text {
                    width: parent.width
                    text: presentation.slideHeading

                    textFormat: Text.RichText
                    wrapMode: Text.WordWrap

                    font.pixelSize: 28
                    font.bold: true

                    color: "#A78BFA"

                    horizontalAlignment:
                        Text.AlignLeft
                }

                Text {
                    width: parent.width
                    text: presentation.slideBody

                    textFormat: Text.RichText
                    wrapMode: Text.WordWrap

                    font.pixelSize: 17

                    color: "#C4B5FD"

                    horizontalAlignment:
                        Text.AlignLeft
                }

                Text {
                    width: parent.width
                    text:
                        presentation.slideHighlight

                    textFormat: Text.RichText
                    wrapMode: Text.WordWrap

                    font.pixelSize: 18
                    font.bold: true

                    color: "#8B5CF6"

                    horizontalAlignment:
                        Text.AlignLeft
                }
            }
        }

        Item {
            id: mediaPanel

            anchors.left: leftPanel.right
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.bottom: parent.bottom

            Image {
                id: fallbackImage

                source: "slide1.png"

                anchors.fill: parent
                anchors.margins: 10

                fillMode:
                    Image.PreserveAspectFit

                visible:
                    !presentation.remoteAvailable
            }

            Image {
                id: remoteImage

                anchors.fill: parent
                anchors.margins: 10

                fillMode:
                    Image.PreserveAspectFit

                visible:
                    presentation.remoteAvailable &&
                    !presentation.currentIsVideo

                cache: false
            }

            VideoOutput {
                id: videoOutput

                anchors.fill: parent
                anchors.margins: 10

                visible:
                    presentation.remoteAvailable &&
                    presentation.currentIsVideo

                fillMode:
                    VideoOutput.PreserveAspectFit
            }
        }
    }
}
