import unittest, sys, mariadb, os, datetime
from unittest.mock import patch, MagicMock, Mock

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from src.database import DbConnect
from src.main import Main
import sys, io


class testMainTemplateNoEnv(unittest.TestCase):
    tempFileData = None
    capturedOutput = None
    directory = os.getcwd()
    env_path = os.path.join(directory, ".env")

    @classmethod
    def setUpClass(self):
        self.capturedOutput = io.StringIO()
        sys.stdout = self.capturedOutput
        if os.path.isfile(self.env_path):
            f_r = open(self.env_path, "r")
            self.tempFileData = f_r.read()
            f_r.close()
            os.remove(self.env_path)

    @classmethod
    def tearDown(self):
        sys.stdout = sys.__stdout__
        if self.tempFileData is not None:
            f_w = open(self.env_path, "w")
            self.tempFileData = f_w.write(self.tempFileData)
            f_w.close()
        self.capturedOutput = None
        self.tempFileData = None


class testMainTemplateEnv(unittest.TestCase):
    isNotHere = False
    capturedOutput = None
    directory = os.getcwd()
    data = "TOKEN=mokup\n"
    env_path = os.path.join(directory, ".env")

    @classmethod
    def setUpClass(self):
        self.capturedOutput = io.StringIO()
        sys.stdout = self.capturedOutput
        if not os.path.isfile(self.env_path):
            self.isNotHere = True
            f_w = open(self.env_path, "w")
            f_w.write(self.data)
            f_w.close()

    @classmethod
    def tearDown(self):
        sys.stdout = sys.__stdout__
        if self.isNotHere:
            os.remove(self.env_path)
        self.capturedOutput = None


class testMainConstructorArgs(testMainTemplateNoEnv):
    def testCreateMainDefault(self):
        cls = Main()
        cls.setup("TOKEN=test")
        self.assertEqual(
            self.capturedOutput.getvalue(),
            "WARNING !! no database was found, data will only display\n",
        )


class testMainConstructorEnv(testMainTemplateEnv):
    def testCreateMainDefault(self):
        cls = Main()
        cls.setup()
        self.assertEqual(
            self.capturedOutput.getvalue(),
            "WARNING !! no database was found, data will only display\n",
        )


class testMainConstructorError(testMainTemplateNoEnv):
    def testCreateMainDefaultError(self):
        cls = Main()
        with self.assertRaises(Exception) as context:
            cls.setup()

        self.assertTrue("no environment variable was given" in context.exception.args)


class testDatabase(unittest.TestCase):
    mock_database = (
        "database:oxygen, username:root, passwd:password, host:127.0.0.1, port:3306"
    )

    @classmethod
    @patch("src.database.mariadb")
    @patch("src.database.mariadb.connect")
    def setUpClass(self, mock_db, mock_conn):
        mock_db.connect.return_value = mock_conn
        cursor = MagicMock()
        mock_result = MagicMock()
        mock_db.version = "MOCK"
        cursor.__enter__.return_value = mock_result
        cursor.__exit__ = MagicMock()
        mock_conn.cursor.return_value = cursor

    @patch("src.database.mariadb")
    @patch("src.database.mariadb.connect")
    def testConnection(self, mock_db, mock_conn):
        db = DbConnect(self.mock_database)
        self.assertEqual(mock_db.return_value, db.comm)


if __name__ == "__main__":
    result = unittest.main()
    print(result)
