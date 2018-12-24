# MusicDB,  a music manager with web-bases UI that focus on music.
# Copyright (C) 2017,2018  Ralf Stemmer <ralf.stemmer@gmx.net>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
This module takes care that the state of MusicDB will persist over several sessions.
This is not done automatically by the :class:`~MDBState` class.
Each read or write process to the files that hold the state will be triggered by the classes who manage the related information.

The state is stored in several files in a directory that can be configured via ``[server]->statedir``

All files inside the state directory are managed by the :class:`~MDBState` class.
The content of those files should not be changed by any user because its content gets not validated.
"""

from lib.cfg.config import Config
from lib.cfg.csv    import CSVFile
from lib.db.musicdb import MusicDatabase
import time
import logging
import os

class META:
    pass
class QUEUE:
    pass

class MDBState(Config, object):
    """
    This class holds the MusicDB internal state.

    The following table shows which method is responsible for which file in the MusicDB State Directory.

        +------------------------+-------------------------+-------------------------+
        | File Name              | Read Method             | Write Method            |
        +========================+=========================+=========================+
        | songqueue.csv          | :meth:`~LoadSongQueue`  | :meth:`~SaveSongQueue`  |
        +------------------------+-------------------------+-------------------------+
        | artistblacklist.csv    | :meth:`~LoadBlacklists` | :meth:`~SaveBlacklists` |
        +------------------------+-------------------------+-------------------------+
        | albumblacklist.csv     | :meth:`~LoadBlacklists` | :meth:`~SaveBlacklists` |
        +------------------------+-------------------------+-------------------------+
        | songblacklist.csv      | :meth:`~LoadBlacklists` | :meth:`~SaveBlacklists` |
        +------------------------+-------------------------+-------------------------+

    Args:
        path: Absolute path to the MusicDB state directory
        musicdb: Instance of the MusicDB Database (can be None)
    """

    def __init__(self, path, musicdb=None):

        Config.__init__(self, os.path.join(path, "state.ini"))
        self.musicdb = musicdb
        self.path    = path
        self.meta    = META

        self.meta.version = self.Get(int, "meta", "version", 0) # 0 = inf
        if self.meta.version < 2:
            logging.info("Updating mdbstate/state.ini to version 2")
            self.Set("meta", "version", 2)


    def ReadList(self, listname):
        """
        Reads a list from the mdbstate directory.
        The ``listname`` argument defines which file gets read: ``config.server.statedir/listname.csv``.

        This method should only be used by class internal methods.
        When a file can not be accessed, an empty list gets returned.
        So deleting a file is an option to reset an internal state of MusicDB.

        Args:
            listname (str): Name of the list to read without trailing .csv

        Returns:
            A list of rows from the file. When reading the list fails, an empty list gets returned.
        """
        path = os.path.join(self.path, listname + ".csv")

        try:
            csv  = CSVFile(path)
            rows = csv.Read()
        except Exception as e:
            logging.warning("Accessing file \"%s\" failed with error %s", str(path), str(e))
            return []

        return rows


    def WriteList(self, listname, rows):
        """
        This method write a list of rows into the related file.
        The ``listname`` argument defines which file gets written: ``config.server.statedir/listname.csv``.

        This method should only be used by class internal methods.

        Args:
            listname (str): Name of the list to read without trailing .csv
            rows(list): The list that shall be stored

        Returns:
            ``True`` on success, otherwise ``False``
        """
        path = os.path.join(self.path, listname + ".csv")

        if type(rows) != list:
            logging.warning("Expected a list to write into the csv file at \"%s\". Got type \"$s\" instead. \033[1;30m(Will not change the file)", path, str(type(rows)))
            return False

        try:
            csv  = CSVFile(path)
            csv.Write(rows)
        except Exception as e:
            logging.warning("Accessing file \"%s\" failed with error %s", str(path), str(e))
            logging.debug("Data: %s", str(rows))
            return False
        return True


    def LoadSongQueue(self):
        """
        This method reads the song queue from the state directory.

        The method returns the queue as needed inside :meth:`mdbapi.songqueue.SongQueue`:
        A list of dictionaries, each containing the ``entryid`` and ``songid`` as integers and ``israndom`` as boolean.

        The UUIDs of the queue entries remain.

        Returns:
            A stored song queue
        """
        rows  = self.ReadList("songqueue")
        queue = []
        for row in rows:
            try:
                entry = {}
                entry["entryid"]  = int( row["EntryID"])
                entry["songid"]   = int( row["SongID"])
                # Be backwards compatible for lists that have no IsRandom key yet.
                # TODO: DEPRECATED: Remove in December 2019
                if "IsRandom" in row:
                    entry["israndom"] = bool(row["IsRandom"])
                else:
                    entry["israndom"] = False

                queue.append(entry)
            except Exception as e:
                logging.warning("Invalid entry in stored Song Queue: \"%s\"! \033[1;30m(Entry will be ignored)", str(row))

        return queue


    def SaveSongQueue(self, queue):
        """
        This method saves a song queue.
        The data structure of the queue must be exact as the one expected when the queue shall be loaded.

        Args:
            queue (dictionary): The song queue to save.

        Returns:
            *Nothing*
        """
        # transform data to a structure that can be handled by the csv module
        # save entry ID as string, csv cannot handle 128bit integer
        rows = []
        for entry in queue:
            row = {}
            row["EntryID"]  = str(entry["entryid"])
            row["SongID"]   = int(entry["songid"])
            row["IsRandom"] = str(entry["israndom"])

            rows.append(row)

        self.WriteList("songqueue", rows)
        return


    def __LoadBlacklist(self, filename, idname, length):
        # filename: artistblacklist
        # idname:   ArtistID
        if filename not in ["artistblacklist","albumblacklist","songblacklist"]:
            raise ValueError("filename must be \"artistblacklist\", \"albumblacklist\" or \"songblacklist\"")
        if idname not in ["ArtistID","AlbumID","SongID"]:
            raise ValueError("idname must be \"ArtistID\", \"AlbumID\" or \"SongID\"")

        rows      = self.ReadList(filename)
        rows      = rows[:length]   # Do not process more entries than necessary
        blacklist = []
        for row in rows:
            try:
                entry = {}
                if row[idname] == "":
                    entry["id"] = None
                else:
                    entry["id"] = int(row[idname])

                # Be backwards compatible for lists that have no timestamp key yet.
                # TODO: DEPRECATED: Remove in December 2019
                if "TimeStamp" in row:
                    if row["TimeStamp"] == "":
                        entry["timestamp"] = None
                    else:
                        entry["timestamp"] = int(row["TimeStamp"])
                else:
                    entry["timestamp"] = int(time.time())

                blacklist.append(entry)
            except Exception as e:
                logging.warning("Invalid entry in stored blacklist %s: \"%s\"! - Error: \"%s\" \033[1;30m(Entry will be ignored)",
                        filename+".csv", str(row), str(e))

        # Fill the rest of the blacklist, that was not stored in a file
        diff = length - len(rows)
        if diff > 0:
            for _ in range(diff):
                entry = {}
                entry["id"]        = None
                entry["timestamp"] = None
                blacklist.append(entry)
    
        return blacklist

    def LoadBlacklists(self, songbllen, albumbllen, artistbllen):
        """
        This method returns a dictionary with the blacklist managed by :class:`mdbapi.randy.Randy`.
        This method also handles the blacklist length by adding empty entries or cutting off exceeding ones.

        Args:
            songbllen (int): Number of entries the blacklist shall have
            albumbllen (int): Number of entries the blacklist shall have
            artistbllen (int): Number of entries the blacklist shall have

        Returns:
            A dictionary with the blacklists as expected by :class:`mdbapi.randy.Randy`
        """

        blacklists = {}
        blacklists["artists"] = self.__LoadBlacklist("artistblacklist", "ArtistID", artistbllen)
        blacklists["albums"]  = self.__LoadBlacklist("albumblacklist",  "AlbumID",  albumbllen)
        blacklists["songs"]   = self.__LoadBlacklist("songblacklist",   "SongID",   songbllen)
        return blacklists



    def __SaveBlacklist(self, blacklist, filename, idname):
        if filename not in ["artistblacklist","albumblacklist","songblacklist"]:
            raise ValueError("filename must be \"artistblacklist\", \"albumblacklist\" or \"songblacklist\"")
        if idname not in ["ArtistID","AlbumID","SongID"]:
            raise ValueError("idname must be \"ArtistID\", \"AlbumID\" or \"SongID\"")

        rows = []
        for entry in blacklist:
            if entry["id"] == None:
                continue
            row = {}
            row[idname]      = int(entry["id"])
            row["TimeStamp"] = int(entry["timestamp"])

            rows.append(row)

        self.WriteList(filename, rows)
        return

    def SaveBlacklists(self, blacklists):
        """
        This method stores the blacklist in the related CSV files.
        The data structure of the dictionary is expected to be the same, :class:`mdbapi.randy.Randy` uses.

        Args:
            blacklist (dict): A dictionary of blacklists.

        Returns:
            *Nothing*
        """
        self.__SaveBlacklist(blacklists["songs"],   "songblacklist",   "SongID")
        self.__SaveBlacklist(blacklists["albums"],  "albumblacklist",  "AlbumID")
        self.__SaveBlacklist(blacklists["artists"], "artistblacklist", "ArtistID")
        return



    def GetFilterList(self):
        """
        This method returns a list of the activated genre
        The list consists of the names of the genres as configured by the user.
        That are the names returned by :meth:`lib.db.musicdb.MusicDatabase.GetAllTags`.

        The available genres get compared to the ones set in the state.ini file inside the MusicDB State directory.
        If a genre is not defined in the configuration file, its default value is ``False`` and so it is not active.
        Before the comparison, the state file gets reloaded so that external changes get applied directly.

        .. example::

            filter = mdbstate.GetFilterList()
            print(filter) # ['Metal','NDH']
            # Metal and NDH are active, other available genres are not enabled.

        Returns:
            A list of main genre names that are activated
        """
        if not self.musicdb:
            raise ValueError("Music Database object required but it is None.")
        filterlist = []
        genretags   = self.musicdb.GetAllTags(MusicDatabase.TAG_CLASS_GENRE)
        
        self.Reload()
        for tag in genretags:
            state = self.Get(bool, "albumfilter", tag["name"], False)
            if state:
                filterlist.append(tag["name"])

        return filterlist

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

