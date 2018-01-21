![MusicDB Logo](https://rstemmer.github.io/musicdb/landingpage/img/logo.png)

# MusicDB

MusicDB is a music manager with focus on remote access to your music using a WebUI
and [Music Player Daemon (MPD)](https://musicpd.org/) for streaming.
The WebUI is more a presentation of your music than a database frontend.

So, when you are listening to music, you do not work with software.
Instead you explore your music collection.

**For more details, a list of features and screenshots see the start page [rstemmer.github.io/musicdb/](https://rstemmer.github.io/musicdb/index.html).**

---

Until now I spent more than 6 years for developing this awesome software.
Since I finished a first test version, I use it nearly every day.
Time to share it with the world. :smiley:

For news, follow [@MusicDBProject](https://twitter.com/MusicDBProject) on Twitter.


## Breaking News

This section contains some important information on how to update to a next major version.
Furthermore those changes may break scripts you wrote around MusicDB.

Lines starting with **:wrench: Change:** are steps you have to do *before* updating via `install.sh` script.

### 1.x.x -> 2.0.0+

* Signals got replaced by a named pipe
  * New configuration: `[server] -> fifofile=DATADIR/musicdb.fifo`
  * Communication with the server via signals (`SIGTERM`, `SIGUSR1`) is deprecated. Use the named pipe instead. (Commands: `"shutdown"`, `"refresh"`)
  * [:notebook: Details and examples](https://rstemmer.github.io/musicdb/build/html/mdbapi/server.html)
  * **:wrench: Change:** Add the new configuration into your ini file

* [:notebook: database](https://rstemmer.github.io/musicdb/build/html/mod/database.html) module updated
  * *target* parameter removed. Target gets determined by its path.
  * `update` command removed. Use the [:notebook: repair](https://rstemmer.github.io/musicdb/build/html/mod/repair.html) module for updating paths.
  * `remove` command added.


## Social

Providing and maintaining open source software comes with some downsides.
I'd like to know if anyone is using this software, and what you are doing with it. :smiley:

So feel free to follow my project account [@MusicDBProject](https://twitter.com/MusicDBProject) on Twitter
or e-mail me.

In case you find any bugs, please create an Issue.
Feature requests are welcome as well.


# Using MusicDB

This section describes how to install, update and use MusicDB.

## Requirements

I only test with the latest version of the requirements I list below.
If MusicDB breaks when updating dependencies, it's a bug in MusicDB.
In case MusicDB does not run on outdated operating systems, update your system ;)

* A Linux operating system. Tested with:
  * [Arch Linux](https://www.archlinux.org/) for x86-64 (primary test and development system)
  * [Debian](https://www.debian.org/distrib/) for x86-64 (not recommended because it comes with lots of ~~old~~ "stable" software)
  * [Arch Linux ARM](https://archlinuxarm.org/) for Aarch64 with [ODROID-C2](https://wiki.odroid.com/odroid-c2/odroid-c2)
  * [Arch Linux ARM](https://archlinuxarm.org/) for ARMv7 with [Raspberry Pi 3](https://www.raspberrypi.org/products/raspberry-pi-3-model-b/)
* [Python3](https://www.python.org/)
* [Music Player Daemon (MPD)](https://musicpd.org/)
  * You should consider [Icecast](https://icecast.org/) for encrypting the stream
* A modern web browser for accessing the WebUI:
  * [Firefox](https://www.mozilla.org/en-US/) (recommended)
  * [Chrome](https://www.google.com/chrome/index.html) 
  * [Opera](https://www.opera.com/)
* An Unicode capable file system (Any *modern* file system should work)
* A terminal that supports Unicode, with an Unicode capable font configured (I use KDE's [Konsole](https://www.kde.org/applications/system/konsole/) with [Hack](https://sourcefoundry.org/hack/))

The `install.sh` script checks for tools needed to install MusicDB.
Furthermore `musicdb-check.sh` list all tools and Python modules needed by MusicDB.
You can run the check-script at any time. But before working with MusicDB you should install the none-optional dependencies.

Execute `pip install -r requirements.txt` to install a basic set of Python modules needed for MusicDB.


## Download

To get the latest version of MusicDB, clone this repository.
The *master* branch can be considered stable.

```
git clone https://github.com/rstemmer/musicdb.git
```


## Installation and Update

To install MusicDB, read [:notebook: How to Install MusicDB](https://rstemmer.github.io/musicdb/build/html/usage/install.html) in the documentation.

For updating, you can also execute the `install.sh` script.
Read the *Breaking News* for manual steps to do before updating to a new major release.

Updating to the next minor version, simply run `git pull && ./quickupdate.sh` (Be sure you are on the master branch).


## Usage

The start page of [:notebook: MusicDB's Documentation](https://rstemmer.github.io/musicdb/build/html/index.html)
should give you the help you need to start - or at least the links to the chapters they do
(The [:notebook: CLI MODULES chapters)](https://m45ch1n3.de/musicdb/docs/build/html/index.html#musicdb-cli).
The documentation is also made for developers, not only users. So there is much more information than you will need to use MusicDB.


In general, the first steps are the following, after you have done the [:notebook: First Run](https://rstemmer.github.io/musicdb/build/html/usage/install.html#first-run):

1. [:notebook: Add Music](https://rstemmer.github.io/musicdb/build/html/usage/music.html#importing-albums-to-musicdb) to MusicDB
2. [:notebook: Create Genres](https://rstemmer.github.io/musicdb/build/html/mod/genres.html) and sub-genres you want to use to categorize your Music.
3. [:notebook: Create Moods](https://rstemmer.github.io/musicdb/build/html/mod/moods.html) you want to assign to your songs.
4. Open the WebUI in your browser and tag the albums with the genres you created. (Right click on the albums title in the Album View). Then the random song selection process can start working and stops printing warnings.


Finally some helpful hints:

* For security reasons, MusicDB and MPD only accepts connections from localhost by default. Change the [:notebook: WebSocket address configuration](https://rstemmer.github.io/musicdb/build/html/basics/config.html#websocket) and MPDs `bind_to_address` configuration from `127.0.0.1` to `0.0.0.0` to access your music from anywhere.
* Don't be to specific with the genre tags. Tag albums beforehand and songs only when they are currently playing.
* Set mood-flags only for the current playing song.
* Check the [:notebook: Configuration of Randy](https://rstemmer.github.io/musicdb/build/html/basics/config.html#randy) to make sure the random song selection can work with your music collection. When you have a small music collection, decrease the blacklist sizes.


If there are any problems setting up MusicDB, create an issue.


# Development

This section describes how to contribute to this project.


## Documentation

The [:notebook: MusicDB Documentation](https://rstemmer.github.io/musicdb/build/html/index.html) is a good point to start.
There are all concepts, interfaces and details described.

Most important will be the [:notebook: Quick Start Section](https://rstemmer.github.io/musicdb/build/html/index.html#quick-development-start) that points out some chapters to start reading.


## Contributing

Every help is welcome.


### What you can do

* Create an Issue when you find a bug.
* Improve the documentation.
* Suggesting features via Issue.
* See if there is an Issue you are able to fix, or to give hints on how to fix it.


### Before you change code

* Read [:notebook: Working on MusicDB's Code](https://rstemmer.github.io/musicdb/build/html/basics/workflow.html)
* … and [:notebook: Basic Rules for MusicDB](https://rstemmer.github.io/musicdb/build/html/basics/concept.html)
* Branch from *master*.
* Please don't commit *docs/build* for pull requests.


# Versioning and Branches

I work on MusicDB in three sprints per year. Each sprint is about one and a half week long.
The rest of the year I only want to concentrate on fixing critical bugs.
So you better not use any other branch than *master*. :wink:
It is also recommended to update whenever there are changes on *master*, even when there is no new release.

At least one thing can be said for sure: Major releases are not compatible with the previous version.
How to update will be described in the *Breaking News* section at the beginning of this README.


