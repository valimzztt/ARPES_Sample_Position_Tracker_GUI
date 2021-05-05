
# Overview

This page documents the application that Bryan Luu developed during fall 2016.

The aim of the project is to:
- Display a (colour) feed from the camera showing the sample
- Enable user control of camera settings and properties
- Enable user ability to save a camera image to file
- Identify and display information of sample


-----


# Setup

## Python
To allow for easy-to-implement features (especially for lazy lab programmers), the app is coded in Python. 
Follow the steps below to set-up Python correctly.

1. We used Python 3.5 from the Anaconda distribution. Python 3.5 is needed for PyQt5.
    a. Install link: https://www.continuum.io/downloads
    b. Tutorial: https://docs.python.org/3/tutorial/

2. It is also a good idea to install Python 2.7, to compile the pyflycapture2 library to communicate with Point Grey Flea3 cameras. Since it isn't really used anywhere else, you can just create a new environment with conda:
    a. Open the Anaconda Command prompt and create a new environment for Python 2.7: http://conda.pydata.org/docs/py2or3.html#create-a-python-2-7-environment

## Git
We use Git to version-control the project. Git is a version control system that lets developers save states of their project code and is quite ubiquitous in the Software industry nowadays.

The project was created as a Git repository with a remote on the qdg.phas.ubc.ca server. This allows anyone with SSH access to get the repository. You can use git to obtain the project repository to use and develop it. 

Learn more about Git, and practice your git-fu:
- Atlassian Git Tutorials: https://www.atlassian.com/git/tutorials/
- Documentation: https://www.atlassian.com/git/tutorials/

Follow the steps below to setup Git.
1. Install the latest version of Git
    a. Main site:  https://git-scm.com/
2. If using Windows, install TortoiseGit so you don't have to deal with the command-line (unless you want to)
    a. TortoiseGit main site: https://tortoisegit.org/
		
## FlyCapture2 SDK
To communicate with the Point Grey Flea-3 USB camera, you have to install the FlyCapture2 SDK.
https://www.ptgrey.com/flycapture-sdk

## Pyflycapture2
The project uses Python bindings to the FlyCapture2 SDK to communicate with Point Grey's Flea-3 cameras. 
1. You can get it via several ways:


    a. Using Git (recommended):
    - Clone the repository (if you don't know how, you need to read the tutorials above)
    
      - Repository location: https://github.com/jordens/pyflycapture2
      - If using a command-line: `git clone https://github.com/jordens/pyflycapture2`


    b. Using pip:
    - Open a command-line
    
    - Run `pip install pyflycapture2`

	c. There is a new repository (2019) in https://flir.app.box.com/s/433et5x1lvwqu5jki446g2ejhkg1xyyx
	This has not been tested.
	Another repository can be found under https://meta.box.lenovo.com/v/link/view/ea3d78f8daaa499eaff33fef95251b41

2. Ensure the correct compiler is installed for the python you are using


    a. See here: https://wiki.python.org/moin/WindowsCompilers
3. Next, the library itself must be compiled using python.


    a. Open a command-line in python 3.5 and follow the README.md instructions:
    `pip install cython`
    `pip install numpy`

    Navigate to the repository
    `cd pyflycapture2`

    `python setup.py install`

    From <https://github.com/jordens/pyflycapture2> 


    b. If that doesn't work, activate the python 2.7 library and try again.

## PyQt5
These are the bindings to the Qt-Library. Qt is a set of ubiquitous tools for GUI development which works beautifully and is easy to learn.

Useful info:
- Qt5 Documentation: 
  - http://doc.qt.io/qt-5/
- PyQt5 tutorial
  - http://zetcode.com/gui/pyqt5/

Install both Qt and PyQt5 from this website:
- https://www.riverbankcomputing.com/software/pyqt/download5

## Open CV
To install Open CV, follow these steps on this link (if you are using Linux, if not there are other tutorials by the same author): <http://www.pyimagesearch.com/2016/10/24/ubuntu-16-04-how-to-install-opencv/>

## PyCharm
PyCharm is a fantastic IDE from Jetbrains which integrates well with the Anaconda package, Git, and generally is one of the best IDE's out there. Use of PyCharm is completely optional, but recommended.

- Install PyCharm here:

  - https://www.jetbrains.com/pycharm/download/
		

## Project
Finally, to install the project, clone the repository from the Gogs server:

- `git clone https://qmat-code.phas.ubc.ca:2633/giorgio/CVSampler.git`
