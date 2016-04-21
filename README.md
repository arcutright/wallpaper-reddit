#About
**Warning**: this is a fork of https://github.com/markubiak/wallpaper-reddit/

wallpaper-reddit is a Python 3 program that sets your wallpaper to the top image (or random image) of one or multiple subreddits, configurable in the config file. It can also be used as a mass download tool to automate the collection of images from subreddits using the `-m` flag, can resize downloaded images automatically, and can filter what images to download based on their dimensions. There are many options and a lot of customization is available, check the config file or `--help` for more information.


#Changes from original
- changed default behavior under XFCE to be more VM-friendly
- changed behavior so `--random` flag picks a random image from a random subreddit
- added config flags for randomsub (choose random subreddit), randomlink (choose random image)
- added `--repeat [N]` flag so that the command can be repeated without need for bash commands
- added `-m [N]` "mass download" flag to facilitate image farming (N per subreddit)
- added `-i` "ignore size" flag so that the user can choose to download all images available with `-m`
- many other things, such as threading with `-t [N]`, etc. Check `--help` for a full listing of commands

#Installation
From Source:  

* Dependencies:
    - python3, python-pillow, python-setuptools
* Install dependencies if needed:
    - Ubuntu/Linux Mint/ElementaryOS: `sudo apt-get install python3-dev python3-setuptools libjpeg8-dev zlib1g-dev libfreetype6-dev`  
    - Fedora: `sudo dnf install python3-imaging` (installed by default)  
    - Arch: `sudo pacman -S python-pillow python-setuptools`  
* Clone the repository and navigate into the directory with the setup.py file.  
* Run `sudo python3 setup.py install`  

#Usage
The script is very simple to use.  Simply type:

  `wallpaper-reddit [subreddits] [flags]`
  
If no arguments are specified, the script will default to the top image from a random subreddit (defined in the subs section of the config file, there are several subs by default).  There are many, many more options, all of which you can see by typing:

  `wallpaper-reddit --help`

#Configuration
The config file is in ~/.config/wallpaper-reddit, and will be created automatically.  Currently, the GNOME, XFCE, MATE, Unity, and Cinnamon Desktop Environments should be automatically detected and the program should set the wallpaper without any extra work.  However, due to the varying nature of window managers, it is possible, even likely, that you may have to specify a custom command to set your wallpaper.  The program will prompt you for this if this is the case; the exact command can be researched per desktop environment.  If your desktop environment is not supported, please file an issue so that automatic support can be implemented for others.  

Config Options:  

- `minwidth` and `minheight` set the minimum dimensions the program will consider a valid candidate for a wallpaper.  If `--resize` is enabled, the script will resize the image to those dimensions before setting the wallpaper.
- `maxlinks` is the maximum number of links the script will go through before giving up.
- `resize` does the same thing as the `--resize` flag.  It is enabled by default.
- `randomsub` will choose a random subreddit from the list of subreddits. It is enabled by default.
- `randomlink` will choose a random link from the subreddit's json file. It is disabled by default.
There are probably some I've forgotten, check `reddit-wallpaper -h` or `--help` for a full listing

#Startup
If `wallpaper-reddit` is run with the `--startup` flag, the program will wait on an internet connection.  Options for the startup can only be set in the config file.  They are under the [Startup] section: interval and attempts.  The script will try to make a connection to reddit.com up to $attempts times at every $interval seconds.  For example, the default setting is an interval of 3 and 10 attempts, so the script will try to connect to reddit every 3 seconds for up to 10 tries, giving a total of 30 seconds before the scrpit gives up.  As a reminder, this feature is only activated by the `--startup` flag

#Overlay Titles
The program has an option to overlay the title of the image directly onto the image itself, so using conky to constantly read the title of the image from ~/.wallpaper/title.txt is no longer necessary (although it still works, and is recommended if not using the "resize" option).  This function is not enabled by default, but it can be enabled with either the `--settitle` flag or more permanently in the config under the "Title Overlay" section.  There are five options for setting titles: size, x/y alignment, and x/y offset.  The size (titlesize) is the height of the text in pixels.  To set where the title is aligned (replaces titlegravity) titlealignx can be left, center, or right; titlealigny can be top or bottom.  To offset the title slightly, titleoffsetx and titleoffsety are offsets from the edge of the screen in pixels.  All of these options can only be set in the config file.

#Saving
If `wallpaper-reddit` is run with the `-s` or `--save` flag, no wallpaper will be downloaded.  The current wallpaper will be copied to the save directory, as specified in the config file (default is ~/Pictures/Wallpapers on Linux, ~/My Pictures/Wallpapers on Windows), and its title will be put into a titles.txt file inside the same directory.
If `wallpaper-reddit` is run with the `-a` or `--autosave` flag, it will download a new wallpaper, set it as your
background, and then save a copy to the save directory.

#Blacklists
There is a function to blacklist a certain wallpaper from the script if it is particularly ugly.  Simply run the script with the `--blacklist` flag.  The script will run as usual, but additionally blacklist your current wallpaper.  You'll get a new wallpaper and never see the old one again.

#External commands and wallpaper info
Because more information is always better, much more than the wallpaper itself exists in ~/.wallpaper.

- blacklist.txt contains the urls of blacklisted wallpapers, one can manually add urls without issue.
- url.txt is the url of the current wallpaper
- title.txt is the title of the current wallpaper (useful if you want to put the title into conky)
- external.sh is a bash script that is run at the end of every execution of the script (Linux only).  Any extra commands to deal with the wallpaper can be safely placed in this bash script.  I personally have mine darken my xfce4-panel if the wallpaper is too bright at the top, and set the wallpaper as my SLiM/xscreensaver background.

#Contact
If there is an issue with the program, please file a bitbucket issue.  It doesn't matter how small, if I have free time, I will try to repair it. Please provide as much information as you can (OS, window manager, etc).