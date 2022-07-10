import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        '''self.database_path = "postgresql://{}:{}@{}/{}".format(
            "postgres",
            "postgres",
            "localhost:5432",
            self.database_name)'''

        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
        
        # Test data
        self.added_question_id = None
        self.new_question = {
            "id": 1, 
            "question":"this is a question?", 
            "category": 2, 
            "answer":"answer1",
            "difficulty": 4}
        self.search_term = "actor"
        self.question_id = 1
        self.quiz_body = {"previous_questions": [],
                        "quiz_category": {"type":"science", "id":"1"}}

    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test 
    for successful operation and for expected errors.
    """
    
    def test_get_paginated_questions(self):
        res = self.client().get("/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["questions"]))

    def test_delete_individual_question(self):
        res = self.client().delete(f"/questions/{self.question_id}")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)

    def test_405_delete_questions(self):
        res = self.client().delete(f"/questions")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 405)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "method not allowed")

    def test_405_post_method_on_individual_question(self):
        res = self.client().post("/questions/5")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 405)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "method not allowed")

    def test_create_new_question(self):
        res = self.client().post("/questions", json = self.new_question)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["created"])
        self.added_question_id = data.get("created", None)

    def test_400_create_new_question_without_body(self):
        res = self.client().post("/questions")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "bad request")

    def test_get_questions_by_category(self):
        res = self.client().get("categories/2/questions")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["questions"]))
        self.assertTrue(len(data["categories"]))
        self.assertTrue(["current_category"])

    def test_search_question(self):
        res = self.client().post("/questions", json={"searchTerm":self.search_term})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(len(data["questions"]))

    def test_get_quiz_question(self):
        res = self.client().post("/gameplay", json=self.quiz_body)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["question"])

    def test_400_get_quiz_without_body(self):
        res = self.client().post("/gameplay")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "bad request")



# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()