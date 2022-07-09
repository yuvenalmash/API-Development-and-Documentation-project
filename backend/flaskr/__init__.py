#from crypt import methods
import os
from sre_parse import CATEGORIES
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    #Allow '*' for origins.
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})


    # after_request decorator to set Access-Control-Allow
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
        return response


    # endpoint to GET requests for all available categories.
    @app.route('/categories', methods = ['GET'])
    def get_categories():
        categories = Category.query.order_by(Category.id).all()

        if len(categories) == 0:
            abort(404)

        categories_dict = {}
        for category in categories:
            categories_dict[category.id] = category.type

        return jsonify({
                "success": True,
                "categories": categories_dict,
                "total_categories": len(categories),
            })


    # handle pagination
    def paginate_questions(request, selection):
        page = request.args.get("page", 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE

        questions = [question.format() for question in selection]
        current_questions = questions[start:end]

        return current_questions


    # endpoint to handle GET requests for questions.
    @app.route('/questions',methods=["GET"])
    def get_questions(category = "all"):
        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)

        if len(current_questions) == 0:
            abort(404)

        return jsonify({
            "success": True,
            "questions": current_questions,
            "total_questions": len(current_questions),
            "current_category": category,
            "categories": get_categories().json["categories"],
            })


    # endpoint to DELETE question using a question ID.
    @app.route('/questions/<int:question_id>',methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.filter(Question.id == question_id).one_or_none()
            if question is None:
                abort(404)

            question.delete()
            selection = question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)

            return jsonify({
                    "success": True,
                    "deleted": question_id,
                    "books": current_questions,
                    "total_books": len(Question.query.all()),
                })

        except:
            abort(422)


    # endpoint to POST a new question.
    @app.route('/questions',methods=["POST"])
    def post_question():
        body = request.get_json()
        if not body:
            abort(400)

        try:
            new_question = body.get("question", None)
            new_answer = body.get("answer", None)
            new_category = body.get("category", None)
            new_difficulty = body.get("difficulty", None)
            if new_question == "" or new_answer == "":
                abort(422)
        except:
            abort(400)

        question = Question(new_question, 
                            new_answer,
                            new_category,
                            new_difficulty)
        question.insert()

        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)

        return jsonify({
                    "success": True,
                    "created": question.id,
                    "questions": current_questions,
                    "total_questions": len(current_questions),
                })


    # endpoint to get questions based on a search term.
    @app.route('/questions/search',methods=["POST"])
    def search_question():
        search_term = request.json.get('searchTerm')
        selection = Question.query.filter(
            Question.question.ilike(f"%{search_term}%")).all()
        if len(selection) == 0:
            abort(404)
        current_questions = paginate_questions(request, selection)

        return jsonify({
                    "success": True,
                    "questions": current_questions,
                    "total_questions": len(current_questions),
                })


    # endpoint to get questions based on category.
    @app.route('/categories/<int:category_id>/questions',methods=["GET"])
    def get_questions_by_category(category_id):
        selection = Question.query.filter(
            Question.category == category_id).all()
        if len(selection) == 0:
            abort(404)
        current_questions = paginate_questions(request,selection)

        return jsonify({
                "success": True,
                "questions": current_questions,
                "total_questions": len(current_questions),
                "category": category_id
            })


    # endpoint to get questions to play the quiz.
    @app.route('/gameplay',methods=["POST"])
    def play():
        previous_questions = request.json.get('previous_questions', [])
        quiz_category = request.json.get('quiz_category', None)

        if (quiz_category is None) or (previous_questions is None):
            abort(400)
        elif (quiz_category['id'] == 0):
            questions = Question.query.all()
        else:
            questions = Question.query.filter_by(
                category=quiz_category['id']).all()

        total_questions = len(questions)

        def random_question():
            return questions[random.randrange(0, total_questions, 1)]

        def check_if_used(question):
            used = False
            for question_ in previous_questions:
                if (question_ == question.id):
                    used = True
            return used

        question = random_question()

        while (check_if_used(question)):
            question = random_question()
            if (len(previous_questions) == total_questions):
                return jsonify({
                    'success': True
                })

        return jsonify({
            'success': True,
            'question': question.format()
        })


    # error handlers for all expected errors
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404, 
            "message": "resource not found"
            }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False, 
            "error": 422, 
            "message": "unprocessable"
            }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False, 
            "error": 400, 
            "message": "bad request"
            }), 400


    return app
