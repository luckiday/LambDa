<div id="top"></div>
<!--
*** Thanks for checking out the Best-README-Template. If you have a suggestion
*** that would make this better, please fork the repo and create a pull request
*** or simply open an issue with the tag "enhancement".
*** Don't forget to give the project a star!
*** Thanks again! Now go create something AMAZING! :D
-->



<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]



<!-- PROJECT LOGO -->
<br />
<div align="center">
  <!-- <a href="https://github.com/luckiday/LambDa">
    <img src="images/logo.png" alt="Logo" width="80" height="80">
  </a> -->

<h3 align="center">LambDa</h3>

  <p align="center">
    A mobile render farm
    <br />
    <!-- <a href="https://github.com/luckiday/LambDa"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/luckiday/LambDa">View Demo</a>
    ·
    <a href="https://github.com/luckiday/LambDa/issues">Report Bug</a>
    ·
    <a href="https://github.com/luckiday/LambDa/issues">Request Feature</a> -->
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About the Project</a>
      <!-- <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul> -->
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#compatibility">Compatibility</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <!-- <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li> -->
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <!-- <li><a href="#acknowledgments">Acknowledgments</a></li> -->
  </ol>
</details>



<!-- ABOUT THE PROJECT -->

## About the Project

LambDa is a distributed system for rendering with Blender. It is designed for use on mobile devices.

LambDa has three components: the server, the workers, and the requesters. The server is intended to run on a
laptop/desktop, the workers on mobile (Android) devices, and the requester anywhere a rendering job originates.

When a requester submits a Blender job to the server as a .blend file, the server divides up the rendering work among
all connected worker devices on a frame-by-frame basis. It collects the output PNG images, and when all the frames have
been rendered, it returns the images to the requester.

<!-- [![Product Name Screen Shot][product-screenshot]](https://example.com)

Here's a blank template to get started: To avoid retyping too much info. Do a search and replace with your text editor 
for the following: `github_username`, `repo_name`, `email_client`, `email`, `project_title`, `project_description` -->

<p align="right">(<a href="#top">back to top</a>)</p>




<!-- GETTING STARTED -->

## Getting Started

Follow these steps to get the server, workers, and requesters up and running.

### Prerequisites

To run a LambDa server or requester, all that is needed is a device with Python installed. The LambDa worker requires
Python and Blender.

To run the LambDa worker in a mobile environment, you will need to install a Linux distribution on an Android device. We
recommend using [Andronix](https://play.google.com/store/apps/details?id=studio.com.techriz.andronix&hl=en_US&gl=US) to
obtain Linux and [Termux](https://f-droid.org/en/packages/com.termux/) for a mobile command line. Install Andronix from
the Google Play Store and Termux from F-Droid, a third-party app store. (Installing Termux from the Play Store will not
work.)

Follow the instructions in Andronix to install **Arch Linux** on your device.

<!-- We have also tested LambDa on Ubuntu, however, recent versions of Blender (3+) are not available from the Ubuntu package
manager. -->

If you want to interact with the Linux GUI on the mobile device, you will also need to
install [VNC Viewer](https://play.google.com/store/apps/details?id=com.realvnc.viewer.android&hl=en_US&gl=US). After you
have set up the Linux distribution using Andronix and Termux, go to Termux and enter the command `vncserver-start`. You
will need to provide a PIN number the first time you run this command. Then open VNC Viewer and connect to `localhost:1`
. Enter the PIN you set. You should now have access to the Linux GUI.

To install Blender, run
`sudo pacman -S blender`.
Once you have installed Blender, you should also
be able to start the Blender GUI through VNC Viewer.

### Compatibility

LambDa has been tested with the following configurations, but we expect it to work with any device running Python 3 and
Blender 2.82, 3.1.2.

**Server/Requester:**

* Linux/Windows/macOS
* Python 3

**Workers:**

* Ubuntu 20.04 (Andronix), Arch Linux ARM (Andronix)
* Blender 2.82, 3.1.2
* Python 3

Any version of Blender since 2.82 (and possibly earlier) will work, but note that the system can only render a model if
the oldest Blender version on any worker is at least as new as the Blender version that generated the Blend file.

### Installation

#### Arch Linux

1. Install dependencies
    ```
    sudo pacman -S git
    sudo pacman -S blender
    ```

2. Download the Lambda repo
    ```
    git clone https://github.com/luckiday/LambDa.git
    ```

#### Ubuntu

1. Install Blender
    ```sh
    sudo apt install blender
    ```

2. Download the Lambda repo
    ```
    git clone https://github.com/luckiday/LambDa.git
    ```

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->

## Usage

<!-- Use this space to show useful examples of how a project can be used. Additional screenshots, code examples and 
demos work well in this space. You may also link to more resources. -->

### Server

Start the server by running

```
cd src/server
python3 server.py
```

The server starts on port 4455. If necessary, the port number the server uses can be changed by modifying the line
in `server.py` that starts with `PORT =`. You may need to modify your device's firewall settings to allow connections on
this port.

The server can be terminated at any time with Ctrl-C, however, this will not stop any worker or requester processes on
any device. Resuming a job after the server restarts is not supported.

### Worker

The worker needs to know the IP address of the server to connect to. Enter the address after the option `--serv-addr` on
the command line when starting `worker.py`. If none is provided, the worker will use the IP address of the machine it is
running on. The server's IP address will be displayed on the server's console after starting it.

If the server's port number was changed from the default, the port number must also be changed in worker.py in the line
that starts with `PORT =`.

After the server has been started, start each worker by running

```
cd src/worker
python3 worker.py --serv-addr [SERVER_IP_ADDRESS]
```

The worker can be terminated with Ctrl-C, but note that terminating a worker before it has completed the work assigned
to it will cause the job to fail, and the cluster will need to be restarted.

### Requester

To request a project to be rendered, locate the .blend file, then run

```
cd src/requester
python3 requester.py <PATH_TO_BLEND_FILE.blend> --serv-addr [SERVER_IP_ADDRESS]
```

The IP address of the server to connect to is configured the same way as in the worker.

Note that the workers must have joined the render farm before the requester can start.

On the requester device, your project's output will end up in

```
├── requester
│   ├── random_proj_name
│   │   ├── outputs
│   │   │   ├── 0001.jpg
│   │   │   ├── ...and so on
```

<!-- _For more examples, please refer to the [Documentation](https://example.com)_ -->

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- ROADMAP -->

## Roadmap

- [x] Render farm with Blender 2.8
- [x] Render farm for Blender 3.x
- [x] Updated [Installation Guide](doc/instruction.md) for Blender 3.x

<!-- See the [open issues](https://github.com/luckiday/LambDa/issues) for a full list of proposed features (and known issues).

 <p align="right">(<a href="#top">back to top</a>)</p> -->



<!-- CONTRIBUTING -->
<!-- ## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request -->

<!-- <p align="right">(<a href="#top">back to top</a>)</p> -->



<!-- LICENSE -->

## License

Distributed under the MIT License. See `LICENSE` for more information.

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- CONTACT -->

## Contact

<!-- Your Name - email@email_client.com -->

Project Link: [https://github.com/luckiday/LambDa](https://github.com/luckiday/LambDa)

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- ACKNOWLEDGMENTS -->
<!-- ## Acknowledgments

* []()
* []()
* []()

<p align="right">(<a href="#top">back to top</a>)</p> -->



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->

[contributors-shield]: https://img.shields.io/github/contributors/luckiday/LambDa.svg?style=for-the-badge

[contributors-url]: https://github.com/luckiday/LambDa/graphs/contributors

[forks-shield]: https://img.shields.io/github/forks/luckiday/LambDa.svg?style=for-the-badge

[forks-url]: https://github.com/luckiday/LambDa/network/members

[stars-shield]: https://img.shields.io/github/stars/luckiday/LambDa.svg?style=for-the-badge

[stars-url]: https://github.com/luckiday/LambDa/stargazers

[issues-shield]: https://img.shields.io/github/issues/luckiday/LambDa.svg?style=for-the-badge

[issues-url]: https://github.com/luckiday/LambDa/issues

[license-shield]: https://img.shields.io/github/license/luckiday/LambDa.svg?style=for-the-badge

[license-url]: https://github.com/luckiday/LambDa/blob/master/LICENSE.txt

[product-screenshot]: images/screenshot.png