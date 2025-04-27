from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from bson.objectid import ObjectId
from app.forms import RecipeForm, ReviewForm
from app.models import Recipe, Review, User
from app import db
from datetime import datetime
from app.forms import DeleteForm

views = Blueprint('views', __name__)

@views.route('/')
def index():
    return redirect(url_for('views.recipes'))

@views.route('/recipes')
def recipes():
    recipe_list = Recipe.get_all(db)
    delete_form = None  # Ensure it's always defined

    if current_user.is_authenticated:
        delete_form = DeleteForm()

        user_data = db.users.find_one({'_id': ObjectId(current_user.id)})
        current_user.saved_recipes = user_data.get('saved_recipes', [])

    current_year = datetime.now().year
    return render_template('recipes.html', recipes=recipe_list, delete_form=delete_form, current_year=current_year)

@views.route('/recipe/<recipe_id>', methods=['GET', 'POST'])
def recipe_detail(recipe_id):
    recipe = Recipe.get_by_id(db, recipe_id)
    delete_form = DeleteForm()  # Always define delete_form

    if not recipe:
        flash('Recipe not found.', 'danger')
        return redirect(url_for('views.recipes'))

    form = ReviewForm()

    if form.validate_on_submit() and current_user.is_authenticated:
        if recipe.author_id == current_user.id:
            flash("You can't review your own recipe.", "warning")
        else:
            # Check if user has already reviewed
            existing_review = db.reviews.find_one({
                'recipe_id': ObjectId(recipe_id),
                'user_id': ObjectId(current_user.id)
            })

            if existing_review:
                # Update the existing review
                db.reviews.update_one(
                    {'_id': existing_review['_id']},
                    {'$set': {
                        'rating': form.rating.data,
                        'comment': form.comment.data,
                        'updated_at': datetime.utcnow()
                    }}
                )
                flash('Your review has been updated.', 'success')
            else:
                # Add new review
                Review.add_review(db, {
                    'recipe_id': ObjectId(recipe_id),
                    'user_id': ObjectId(current_user.id),
                    'username': current_user.username,
                    'comment': form.comment.data,
                    'rating': form.rating.data,
                    'created_at': datetime.utcnow()
                })
                flash('Thanks for your review!', 'success')

        return redirect(url_for('views.recipe_detail', recipe_id=recipe_id))

    reviews = Review.get_reviews_for_recipe(db, recipe_id)
    avg_rating = Review.get_average_rating(db, recipe_id)

    return render_template(
        'recipe_detail.html',
        recipe=recipe,
        delete_form=delete_form,
        form=form,
        reviews=reviews,
        avg_rating=avg_rating
    )

@views.route('/add-recipe', methods=['GET', 'POST'])
@login_required
def add_recipe():
    form = RecipeForm()
    if form.validate_on_submit():
        data = {
            'title': form.title.data,
            'description': form.description.data,
            'ingredients': [i.strip() for i in form.ingredients.data.splitlines()],
            'steps': [s.strip() for s in form.steps.data.splitlines()],
            'image_url': form.image_url.data.strip(),
            'tags': [t.strip() for t in form.tags.data.split(',')],
            'author_id': ObjectId(current_user.id)
        }
        Recipe.create(db, data)
        flash('Recipe added successfully!', 'success')
        return redirect(url_for('views.recipes'))
    return render_template('add_edit_recipe.html', form=form, edit=False)

@views.route('/edit-recipe/<recipe_id>', methods=['GET', 'POST'])
@login_required
def edit_recipe(recipe_id):
    recipe = Recipe.get_by_id(db, recipe_id)
    if not recipe or recipe.author_id != current_user.id:
        flash('Unauthorized or recipe not found.', 'danger')
        return redirect(url_for('views.recipes'))

    form = RecipeForm(obj=recipe)
    if form.validate_on_submit():
        updated_data = {
            'title': form.title.data,
            'description': form.description.data,
            'ingredients': [i.strip() for i in form.ingredients.data.splitlines()],
            'steps': [s.strip() for s in form.steps.data.splitlines()],
            'image_url': form.image_url.data.strip(),
            'tags': [t.strip() for t in form.tags.data.split(',')],
        }
        Recipe.update(db, recipe_id, updated_data)
        flash('Recipe updated.', 'success')
        return redirect(url_for('views.recipe_detail', recipe_id=recipe_id))

    # Prepopulate form
    form.title.data = recipe.title
    form.description.data = recipe.description
    form.ingredients.data = '\n'.join(recipe.ingredients)
    form.steps.data = '\n'.join(recipe.steps)
    form.image_url.data = recipe.image_url or ''
    form.tags.data = ', '.join(recipe.tags)

    return render_template('add_edit_recipe.html', form=form, edit=True)

@views.route('/delete-recipe/<recipe_id>', methods=['POST'])
@login_required
def delete_recipe(recipe_id):
    recipe = Recipe.get_by_id(db, recipe_id)
    if recipe and recipe.author_id == current_user.id:
        Recipe.delete(db, recipe_id)
        flash('Recipe deleted.', 'info')
    else:
        flash('Unauthorized or recipe not found.', 'danger')
    return redirect(url_for('views.recipes'))

@views.route('/toggle-save/<recipe_id>')
@login_required
def toggle_save(recipe_id):
    if recipe_id in current_user.saved_recipes:
        current_user.saved_recipes.remove(recipe_id)
        flash('Recipe removed from saved.', 'info')
    else:
        current_user.saved_recipes.append(recipe_id)
        flash('Recipe saved!', 'success')
    current_user.save_to_db(db)
    return redirect(request.referrer or url_for('views.recipes'))

@views.route('/saved-recipes')
@login_required
def saved_recipes():
    saved = db.recipes.find({'_id': {'$in': [ObjectId(rid) for rid in current_user.saved_recipes]}})
    recipes = [Recipe(r) for r in saved]
    return render_template('saved_recipes.html', recipes=recipes)

@views.route('/delete-review/<review_id>/<recipe_id>', methods=['POST'])
@login_required
def delete_review(review_id, recipe_id):
    review = db.reviews.find_one({'_id': ObjectId(review_id)})

    if review and str(review['user_id']) == current_user.id:
        db.reviews.delete_one({'_id': ObjectId(review_id)})
        flash("Review deleted successfully.", "success")
    else:
        flash("You are not authorized to delete this review.", "danger")

    return redirect(url_for('views.recipe_detail', recipe_id=recipe_id))
