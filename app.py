from flask import Flask, render_template, request, redirect, url_for
import json
import os
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

DATA_FILE = 'recipes.json'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def load_recipes():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []


def save_recipes(recipes):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(recipes, f, ensure_ascii=False, indent=4)


@app.route('/')
def index():
    recipes = load_recipes()
    featured_recipes = recipes[-6:] if len(recipes) > 6 else recipes
    return render_template('index.html', title='Главная', featured_recipes=featured_recipes)


@app.route('/explore')
def explore():
    recipes = load_recipes()
    return render_template('browse.html', recipes=recipes, title='Исследовать')


@app.route('/recipe/<int:recipe_id>')
def view_recipe(recipe_id):
    recipes = load_recipes()
    recipe = next((r for r in recipes if r['id'] == recipe_id), None)

    if not recipe:
        return redirect(url_for('explore'))

    return render_template('recipe_detail.html', recipe=recipe, title=recipe['title'])


@app.route('/create', methods=['GET', 'POST'])  # Исправлено methods
def create_recipe():
    if request.method == 'POST':
        title = request.form.get('title')
        category = request.form.get('category')
        ingredients = [ing.strip() for ing in request.form.get('ingredients').split('\n') if ing.strip()]
        instructions = [inst.strip() for inst in request.form.get('instructions').split('\n') if inst.strip()]

        photo_paths = []
        if 'photos' in request.files:
            files = request.files.getlist('photos')
            for i, file in enumerate(files[:5]):
                if file and file.filename and allowed_file(file.filename):
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"{timestamp}_{i}_{secure_filename(file.filename)}"
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)
                    photo_paths.append(f"uploads/{filename}")

        new_recipe = {
            'id': len(load_recipes()) + 1,
            'title': title,
            'category': category,
            'ingredients': ingredients,
            'instructions': instructions,
            'photos': photo_paths,
            'created_at': datetime.now().strftime("%d.%m.%Y %H:%M")
        }

        recipes = load_recipes()
        recipes.append(new_recipe)
        save_recipes(recipes)

        return redirect(url_for('view_recipe', recipe_id=new_recipe['id']))

    return render_template('create.html', title='Создать рецепт')


@app.route('/about')
def about():
    return render_template('about.html', title='О проекте')


if __name__ == '__main__':
    if not os.path.exists(DATA_FILE):
        save_recipes([])
    app.run(debug=True, host='0.0.0.0', port=5000)