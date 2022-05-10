## Install Blender on Android

This is an installation guide for Blender 3.x on Android.

### Install Apps

Install
[Andronix](https://play.google.com/store/apps/details?id=studio.com.techriz.andronix&hl=en_US&gl=US)
from the Google Play Store.

Install
[VNC Viewer](https://play.google.com/store/apps/details?id=com.realvnc.viewer.android&hl=en_US&gl=US)
from the Google Play Store.

Install [Termux](https://f-droid.org/en/packages/com.termux/) from F-Droid.
You will likely need to enable installations from unknown sources in your
device settings before installing it.
Installing Termux from the Play Store will not work.

### Set up Arch Linux

Open Andronix and select Arch Linux (the white triangle on a blue background).

Select **Proceed**, then **Install**.

Select **Desktop Environment**, then **XFCE**.

It should now tell you that a command has been copied to your clipboard. Tap
**Open Termux** and you will be taken to the Termux command line, where you
should paste and run the command. This will set up and start Arch Linux.

### Using Arch Linux After Installation

After setting up Arch Linux with the Andronix command the first time, you can
start Arch Linux by opening **Termux** and running the command

```./start-arch.sh```

You should then start the VNC server, or stop it and restart it if it was not
stopped previously (this has caused issues):

```vncserver-stop```

```vncserver-start```

### Install Blender

Blender is available through the Arch Linux package manager, pacman.
Blender 3.1.2 is available as of April 3, 2022.

To install Blender, run

```sudo pacman -Sy```

```sudo pacman -S blender```

To verify that it was installed, run

```blender --version```

### Using Blender

LambDa interacts with Blender through the command line interface.
The Blender CLI documentation is available here:
[Command Line Rendering - Blender Manual](https://docs.blender.org/manual/en/latest/advanced/command_line/render.html).

The Blender commands used by LambDa are of the form:

```blender -b <FILENAME>.blend -o //<OUTPUT_NAME> -E <ENGINE> -s <START_FRAME> -e <END_FRAME> -a```

### Blender GUI

To interact with the Blender GUI, start Arch Linux and the VNC server, then open
**VNC Viewer**.

In **VNC Viewer**, tap the plus button to add a new connection.

For the **Address**, enter `localhost:1`. Choose a name, then tap **Create**, then **Connect**.

When you set up Arch Linux initially (or the first time you ran
`vncserver-start`), you should have set a PIN number. Enter that PIN now.

You should now be able to interact with the Arch Linux GUI and start Blender
like normal.
