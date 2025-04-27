from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
from datetime import datetime


class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data['_id'])
        self.username = user_data['username']
        self.email = user_data['email']
        self.password_hash = user_data['password']
        self.saved_recipes = [str(rid) for rid in user_data.get("saved_recipes", [])]


    @staticmethod
    def get_by_email(db, email):
        user_data = db.users.find_one({'email': email})
        return User(user_data) if user_data else None

    @staticmethod
    def get_by_id(db, user_id):
        data = db.users.find_one({'_id': ObjectId(user_id)})
        if data:
            data['_id'] = str(data['_id'])
            data['saved_recipes'] = [str(rid) for rid in data.get('saved_recipes', [])]
            return User(data)
        return None


    @staticmethod
    def create(db, username, email, password):
        hash_pw = generate_password_hash(password)
        user_id = db.users.insert_one({
            'username': username,
            'email': email,
            'password': hash_pw
        }).inserted_id
        return User.get_by_id(db, user_id)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @staticmethod
    def get_user_by_id(user_id, db):
        user_data = db.users.find_one({"_id": ObjectId(user_id)})
        return User(user_data) if user_data else None
    
    def save_to_db(self, db):
        db.users.update_one(
            {"_id": ObjectId(self.id)},
            {
                "$set": {
                    "username": self.username,
                    "email": self.email,
                    "password": self.password_hash,
                    "saved_recipes": self.saved_recipes,
                }
            }
        )

class Recipe:
    def __init__(self, data):
        self.id = str(data['_id'])
        self.title = data['title']
        self.description = data['description']
        self.ingredients = data['ingredients']
        self.steps = data['steps']
        self.image_url = data.get('image_url')
        self.author_id = str(data['author_id'])
        self.tags = data.get('tags', [])
        self.timestamp = data.get('timestamp', datetime.utcnow())

    @staticmethod
    def create(db, data):
        data['timestamp'] = datetime.utcnow()
        result = db.recipes.insert_one(data)
        return str(result.inserted_id)

    @staticmethod
    def get_all(db):
        recipes = db.recipes.find().sort('timestamp', -1)
        return [
            Recipe({**r, '_id': str(r['_id']), 'author_id': str(r['author_id'])})
            for r in recipes
        ]

    @staticmethod
    def get_by_id(db, recipe_id):
        recipe = db.recipes.find_one({'_id': ObjectId(recipe_id)})
        if recipe:
            recipe['_id'] = str(recipe['_id'])
            recipe['author_id'] = str(recipe['author_id'])
            return Recipe(recipe)
        return None

    @staticmethod
    def update(db, recipe_id, data):
        db.recipes.update_one({'_id': ObjectId(recipe_id)}, {'$set': data})

    @staticmethod
    def delete(db, recipe_id):
        db.recipes.delete_one({'_id': ObjectId(recipe_id)})

    def to_dict(self):
        return {
            '_id': str(self.id),
            'title': self.title,
            'description': self.description,
            'ingredients': self.ingredients,
            'steps': self.steps,
            'image_url': self.image_url,
            'tags': self.tags,
            'author_id': str(self.author_id),
        }


class Review:
    def __init__(self, data):
        self.id = str(data['_id'])
        self.recipe_id = str(data['recipe_id'])
        self.user_id = str(data['user_id'])
        self.username = data.get('username', 'Unknown')
        self.comment = data['comment']
        self.rating = int(data['rating'])
        self.timestamp = data.get('timestamp', datetime.utcnow())

    @staticmethod
    def add_review(db, data):
        data['timestamp'] = datetime.utcnow()
        if 'username' not in data:
            # Fallback: fetch from users collection
            user = db.users.find_one({'_id': data['user_id']})
            data['username'] = user.get('username', 'Anonymous') if user else 'Anonymous'
        db.reviews.insert_one(data)


    @staticmethod
    def get_reviews_for_recipe(db, recipe_id):
        return [Review(r) for r in db.reviews.find({'recipe_id': ObjectId(recipe_id)}).sort('timestamp', -1)]

    @staticmethod
    def get_average_rating(db, recipe_id):
        pipeline = [
            {'$match': {'recipe_id': ObjectId(recipe_id)}},
            {'$group': {'_id': '$recipe_id', 'avg_rating': {'$avg': '$rating'}}}
        ]
        result = list(db.reviews.aggregate(pipeline))
        return round(result[0]['avg_rating'], 1) if result else None
