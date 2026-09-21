import QtQuick 2.0;
import calamares.slideshow 1.0;

Presentation
{
    id: presentation
    anchors.fill: parent

    Rectangle {
        anchors.fill: parent
        color: "#000000"
        z: -100
    }

    Timer {
        interval: 20000
        repeat: true
        onTriggered: presentation.goToNextSlide()
    }

    Slide {
        Image {
            id: background1
            source: "slide1.png"
            width: 467
            height: 280
            fillMode: Image.PreserveAspectFit
            anchors.centerIn: parent
        }

        Text {
            anchors.horizontalCenter: background1.horizontalCenter
            anchors.top: background1.bottom
            text: qsTr("Welcome to N.E.E.B.L.E.S. OS.<br/>The installation should complete in a few minutes.")
            wrapMode: Text.WordWrap
            width: 600
            horizontalAlignment: Text.Center
            color: "#F5F5F5"
        }
    }
}
