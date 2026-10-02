import QtQuick 2.0
import calamares.slideshow 1.0

Presentation {
    id: presentation
    anchors.fill: parent

    Rectangle {
        anchors.fill: parent
        color: "#000000"
        z: -100
    }

    Slide {
        Item {
            id: leftPanel

            anchors.left: parent.left
            anchors.top: parent.top
            anchors.bottom: parent.bottom

            width: parent.width * 0.25
        }

        Item {
            anchors.left: leftPanel.right
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.bottom: parent.bottom

            Image {
                source: "slide1.png"

                anchors.fill: parent
                anchors.margins: 10

                fillMode:
                    Image.PreserveAspectFit
            }
        }
    }
}
