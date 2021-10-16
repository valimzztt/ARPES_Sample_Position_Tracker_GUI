
# Overview

This page documents the application that Valentina Mazzotti developed during summer 2021. Credits go to Bryan Luu for 
developing part of the GUI. 

The aim of the project is to:
- Enable user control of camera settings and properties
- Enable user ability to save a camera image to file
- Start the camera and measure the shift between consecutive images


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
		
