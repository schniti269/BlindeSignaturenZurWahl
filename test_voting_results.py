import unittest
import json
import os
import shutil
import asyncio
from app.main import get_results, get_voted_students


class TestVotingResults(unittest.TestCase):
    def setUp(self):
        # Backup existing data files if they exist
        self.data_backup = {}
        for file in ["voted.csv", "votes.json", "students.csv"]:
            file_path = f"data/{file}"
            if os.path.exists(file_path):
                with open(file_path, "rb") as f:
                    self.data_backup[file] = f.read()

    def tearDown(self):
        # Restore backup data
        for file, content in self.data_backup.items():
            file_path = f"data/{file}"
            with open(file_path, "wb") as f:
                f.write(content)

    def test_results_function(self):
        # Create test data
        with open("data/votes.json", "w") as f:
            json.dump(
                [
                    {"vote": "Kandidat A", "signature": "123"},
                    {"vote": "Kandidat A", "signature": "456"},
                    {"vote": "Kandidat B", "signature": "789"},
                ],
                f,
            )

        with open("data/students.csv", "w", encoding="utf-8") as f:
            f.write("student1\nstudent2\nstudent3\nstudent4\nstudent5")

        with open("data/voted.csv", "w", encoding="utf-8") as f:
            f.write("student1\nstudent2\nstudent3")

        # Test results function
        result = asyncio.run(get_results())

        # Verify response structure
        self.assertIn("votes", result)
        self.assertIn("participation", result)
        self.assertIn("total_students", result)
        self.assertIn("voted_students", result)

        # Check voting results
        self.assertEqual(result["votes"], {"Kandidat A": 2, "Kandidat B": 1})

        # Check participation
        self.assertEqual(result["total_students"], 5)
        self.assertEqual(result["voted_students"], 3)
        self.assertEqual(result["participation"], 60.0)  # 3/5 * 100 = 60%

    def test_voted_students_function(self):
        # Create test data
        with open("data/voted.csv", "w", encoding="utf-8") as f:
            f.write("student1\nstudent2\nstudent3")

        # Test voted students function
        result = asyncio.run(get_voted_students())

        # Verify response structure
        self.assertIn("voted_students", result)

        # Check voted students list
        self.assertEqual(result["voted_students"], ["student1", "student2", "student3"])


if __name__ == "__main__":
    unittest.main()
