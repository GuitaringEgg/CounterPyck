CounterPyck
===========

Counter pick is a work-in-progress program that shows viable counter picks against the current lineup based on dotabuff's matchup data.

How to Use
-----------
todo

Required Libraries
-----------
If you wish to run this script from the scource files, you'll need the following libraries.
- OpenCV
- Numpy
- Dota2Py

TODO
--------
- ~~Tidy repo~~
- ~~Tidy code into nicer, logical classes and files~~
- ~~Get hero counter picks working based on matchup data~~
- ~~Get it working in the console first~~
- Create the gui
- Make image analyser run in a seperate thread
- Use a better method of getting a screenshot (using ingame screeshot or steam screenshot)
- Display suggested heroes images in GUI
- Fix limitations


Future
---------
- Detect when picking starts and finishes to only analyse when heroes can actually be there
- Auto detect game mode
- Detect different game modes
- **Random draft**
    - Detect pool using grid view and only suggest from pool
- **Captains mode**
    - Suggest bans based on heros that are good against your current team


Known limitations
--------------
- Won't support resolutions other than 1920x1080. Should be easy to alter
- Needs to be focused on window.
- Preliminary matchup analysis is odd. May need a better data source, or use the data better.
- Will only work on dual screen monitors.
