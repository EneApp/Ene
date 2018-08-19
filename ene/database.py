#  ENE, Automatically track and sync anime watching progress
#  Copyright (C) 2018 Peijun Ma, Justin Sedge
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

""" This module handles database access"""
import sqlite3


class Database:
    """
    Class to manage database access
    """
    def __init__(self, location):
        self.connection = sqlite3.connect(location, isolation_level=None)
        self.cursor = self.connection.cursor()
        self.initial_setup()

    def initial_setup(self):
        """
        Sets up the database for use, creating any tables if needed
        """
        script = """
        CREATE TABLE IF NOT EXISTS Show(
            show_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            show_name TEXT UNIQUE
            );
        CREATE TABLE IF NOT EXISTS Episode(
            episode_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            episode_path,
            show_ID REFERENCES Show(show_ID)
            );
        """
        self.cursor.executescript(script)
        self.cursor.execute('PRAGMA foreign_keys = on;')

    def add_show(self, show):
        """
        Inserts a show into the database

        Args:
            show:
                The show to insert into the database
        Returns:
            The row ID of the newly inserted show
        """
        self.cursor.execute('INSERT INTO Show(show_name) VALUES (?)', (show,))
        return self.cursor.lastrowid

    def add_episode_by_show_name(self, episode, show):
        """
        Adds an episode to the database based on its shows name

        Args:
            episode:
                The path of the episode to add
            show:
                The show the episode belongs to

        Returns:
            The row ID of the newly inserted episode
        """
        show_id = self.get_show_id_by_name(show)
        if show_id is None:
            show_id = self.add_show(show)
        return self.add_episode_by_show_id(episode, show_id)

    def add_episode_by_show_id(self, episode, show_id):
        """
        Adds an episode to the database based on its shows ID

        Args:
            episode:
                The path of the episode to add
            show_id:
                The ID of the show the episode belongs to

        Returns:
            The row ID of the newly insert episode
        """
        self.cursor.execute('INSERT INTO Episode(episode_path, show_ID) VALUES(?,?)',
                            (episode, show_id))
        return self.cursor.lastrowid

    def write_all_shows_delta(self, shows):
        """
        Finds the delta of the input shows compared to what is already in the
        database and writes the newly added shows to the database

        Args:
            shows:
                A list of shows to compare and add
        """
        cur = [x[0] for x in self.get_all_shows()]
        delta = (set(shows) - set(cur))
        for show in delta:
            self.add_show(show)

    def write_all_episodes_delta(self, series):
        """
        Finds the delta of the input episodes for each show compared to what is
        already in the database and adds any newly added episodes

        Args:
            series:
                A dictionary with show names as keys and lists of episodes
        """
        for show in series.keys():
            key = self.get_show_id_by_name(show)
            episodes = set([str(x) for x in series[show]])
            cur = set(x[0] for x in self.get_episodes_by_show_id(key))
            delta = episodes - cur
            for episode in delta:
                self.add_episode_by_show_id(str(episode), key)

    def get_show_id_by_name(self, show):
        """
        Looks up the show ID for a given show name

        Args:
            show:
                The show to find the ID of

        Returns:
            The show ID for the show
        """
        self.cursor.execute('SELECT show_ID FROM Show WHERE show_name=?', (show,))
        res = self.cursor.fetchone()
        if res is not None:
            return res[0]
        return None

    def get_episodes_by_show_name(self, show):
        """
        Gets all episodes for a given show using the shows name

        Args:
            show:
                The name of the show

        Returns:
            A list of episodes or None if the show does not exist
        """
        show_id = self.get_show_id_by_name(show)
        if show_id is None:
            return None
        return self.get_episodes_by_show_id(show_id)

    def get_episodes_by_show_id(self, show_id):
        """
        Gets all episodes for a given show using the shows ID

        Args:
            show_id:
                The ID of the show

        Returns:
            A list of episodes for the given show
        """
        self.cursor.execute('SELECT episode_path FROM Episode where show_ID = ?', (show_id,))
        return self.cursor.fetchall()

    def get_all(self):
        """
        Gets all episodes and shows from the database

        Returns:
            A list of tuples with the show name as the first element and the
            episode path as the second element
        """
        self.cursor.execute("""SELECT show_name, episode_path
            FROM Show S
            INNER JOIN Episode E
            ON E.show_ID=S.show_ID""")
        return self.cursor.fetchall()

    def get_all_shows(self):
        """
        Gets all the shows from the database

        Returns:
            A list of tuples containing all shows in the database
        """
        self.cursor.execute('SELECT show_name FROM Show')
        return self.cursor.fetchall()

    def get_all_episodes(self):
        """
        Gets all the episodes from the database

        Returns:
            A list of tuples containing all the episodes in the database
        """
        self.cursor.execute('SELECT episode_path FROM Episode')
        return self.cursor.fetchall()
