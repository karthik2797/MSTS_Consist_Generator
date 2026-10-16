MSTS CONSIST GENERATOR
======================

A simple Indian Railways-inspired Windows GUI utility that creates Microsoft Train Simulator .con consist files from .eng and .wag files in a selected TRAINS\TRAINSET folder.

FEATURES
--------
- Simple Indian Railways-inspired GUI using railway blue, green and saffron; no formation preset buttons.
- Fixed tail-stock detection and added clearer error handling for scanning and writing files.
- Scans .eng and .wag files in the Trainset root and subfolders, using files up to one folder level below the selected Trainset directory.
- Configurable number of consists, filename prefix, locomotive count, passenger-stock count, freight/extra-wagon count, maximum vehicles, speed values and optional random seed.
- Stock mix options: Mixed, Passenger, Freight, or Rolling stock only. Passenger/freight classification uses the same available .wag pool because MSTS filenames do not provide a reliable universal classification.
- Locomotive policies: every consist, some consists, random count, or none.
- Optional SLR/BVZI/caboose/guard van/brake van at the end when detected by filename/folder keywords.
- Optional random counts, repeated-file avoidance and Wagon Flip ( ).
- Generated-file list, open output folder, developer credit, clickable YouTube channel and email links, and Buy Me a Coffee link.

HOW TO RUN
----------
1. Install Python 3 for Windows from https://www.python.org/downloads/windows/ and enable Add Python to PATH.
2. Run MSTS_Consist_Generator.py with Python, or build an EXE using BUILD_EXE_ON_WINDOWS.bat.
3. Select your MSTS TRAINS\TRAINSET folder, review the settings and click GENERATE CONSISTS.
4. Files are written to MSTS_Generated_Consists beside the selected TRAINSET folder.

BUILD A WINDOWS EXE
-------------------
Double-click BUILD_EXE_ON_WINDOWS.bat on a Windows PC with Python installed. It installs PyInstaller and creates dist\MSTS_Consist_Generator.exe.

DOCUMENTATION
-------------
See DISCLAIMER_AND_TERMS.txt for the disclaimer, acceptable-use rules, copyright guidance, redistribution notes, and user responsibilities.

IMPORTANT NOTES
---------------
- The package contains source code and a build script, not a precompiled EXE.
- Tail-stock detection is based on filenames and folder names. Stock naming varies, so inspect generated consists before use.
- The generator writes the .con text structure based on the supplied working examples. Always test generated consists in MSTS before using them in an activity.

Designed and developed by Karthik Iyer - IRTS Fan.
Buy Me a Coffee: https://buymeacoffee.com/irtsfan

YouTube Channel: https://www.youtube.com/@IRTSFAN
Email: irtslover@gmail.com
