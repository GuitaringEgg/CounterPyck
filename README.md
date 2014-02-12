CounterPyck
===========

Counter pick is a work-in-progress program that shows viable counter picks against the current lineup based on dotabuff's matchup data

TODO
--------
- ~~Tidy repo~~
- Tidy code into nicer, logical classes and files
- Make image analyser run in a seperate thread
- Get hero counter picks working based on matchup data
- Get it working in the console first
- Create the gui
- Fixed limitations
- Move all data to appdata? Probably

Future
---------
- Detect when picking starts and finishes to only analyse when heroes can actually be there
- Auto detect game mode
- Detect our selected hero
- Optimise
    - Image resizing may speed up detection, but make it less accurate
- Detect different game modes
- All pick support should be already there
- **Random draft**
    - Detect pool using grid view and only suggest from pool
- **Captains mode**
    - Suggest bans based on heros that are good against your current team
    - Haven't really played captains mode so I'll probably need ideas from other people


Known limitations
--------------
- Won't support resolutions other than 1920x1080. Should be easy to alter
- The code is a mess. The repo is a mess. Needs tidied before continuing
- Needs to be focused on the dota window atm, which isn't ideal. screenshoting the entire screen maybe take too long to analyse. Resize?
- Preliminary matchup analysis is odd. Many negative advantages. Need to consider the data more.
- Will only work on dual screen monitors. Need to find a way to write text on top of other windows to get around that.
