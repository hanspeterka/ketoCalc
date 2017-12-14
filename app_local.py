#!/usr/bin/env python
# -*- coding: utf-8 -*-


# run by pyserver


import bottle
# from bottle import view
from bottle import route, template
from bottle import error, redirect
from bottle import get, post, request
# from bottle import static_file


# Session manager
from beaker.middleware import SessionMiddleware

# MySQL connector
import MySQLdb

# Hashing library
import hashlib

# bottle.TEMPLATE_PATH = "~/Dropbox/Programming/PyServer/views/"
# bottle.TEMPLATE_PATH.insert(0, '/home/jan/Dropbox/Programming/KetoCalc')

bottle.TEMPLATE_PATH.insert(0, '/home/jan/Dropbox/Programming/ketoCalc/views')

session_opts = {
    'session.type': 'file',
    'session.cookie_expires': 60000,
    'session.data_dir': './data',
    'session.auto': True
}


def temp_print(input):
    print(input)


class Diet(object):
    """  For loading from database """

    def __init__(self, dbID, name, sugar, fat, protein):
        super(Diet, self).__init__()
        self.id = dbID
        self.name = name
        self.sugar = sugar
        self.fat = fat
        self.protein = protein


class Recipe(object):
    """  For loading from database """

    def __init__(self, dbID, name):
        super(Recipe, self).__init__()
        self.id = dbID
        self.name = name


class Ingredient(object):
    """  For loading from database """

    def __init__(self, dbID, name, sugar, fat, protein):
        super(Ingredient, self).__init__()
        self.id = dbID
        self.name = name
        self.sugar = sugar
        self.fat = fat
        self.protein = protein
        self.amount = 0


app = SessionMiddleware(bottle.app(), session_opts)


# SESSION related functions
def getSession():
    session = bottle.request.environ.get('beaker.session')
    return session


# DATABASE related functions
def dbConnect():
    db = MySQLdb.connect(user='root', password='mainframe', database='keto_db')
    return db


# Recipes
def loadRecipe(recipeID):
    db = dbConnect()
    cursor = db.cursor()

    query = ("SELECT * FROM recipes WHERE id='{}';".format(recipeID))
    cursor.execute(query)
    response = cursor.fetchone()
    recipe = Recipe(response[0], response[1])

    query = ("SELECT recipes_has_ingredients.ingredients_id FROM recipes_has_ingredients WHERE recipes_has_ingredients.recipes_id='{}';".format(recipeID))
    cursor.execute(query)
    response = cursor.fetchall()

    ingredientIDs = []
    for i in range(len(response)):
        ingrID = response[i][0]
        ingredientIDs.append(ingrID)

    return [recipe, ingredientIDs]
    """ recipe (Recipe: id, name); ingredientIDs (Array: ingredientID (Int))"""


def saveRecipe(recipe, ingredients, dietID):
    """ recipe (Object: name), ingredients (Array of ingredient (Object: id, amount), dietID (Int)"""

    db = dbConnect()
    cursor = db.cursor()

    """ Save to recipe table """
    query = ("INSERT INTO recipes(name) VALUES ('{}');".format(recipe.name))
    cursor.execute(query)
    last_id = db.insert_id()

    """ Save to recipe/ingredient table"""
    for ingredient in ingredients:
        query = ("INSERT INTO recipes_has_ingredients(recipes_id, ingredients_id, amount) VALUES({}, {}, {})".format(last_id, ingredient.id, ingredient.amount))
        cursor.execute(query)

    """ save to diet/recipe table"""
    query = ("INSERT INTO diets_has_recipes(diets_id, recipes_id) VALUES ({}, {});".format(dietID, last_id))
    cursor.execute(query)

    db.commit()

    return last_id


def loadUserRecipes(username):
    db = dbConnect()
    cursor = db.cursor()
    temp_query = ("SELECT users.id FROM users WHERE users.username = '{}';".format(username))
    cursor.execute(temp_query)
    user_id = cursor.fetchone()

    query = ("SELECT recipes.id, recipes.name FROM recipes JOIN diets_has_recipes ON recipes.id=diets_has_recipes.recipes_id JOIN diets ON diets.id=diets_has_recipes.diets_id JOIN users_has_diets ON diets.id=users_has_diets.diets_id JOIN users ON users_has_diets.users_id= '{}';".format(user_id[0]))
    cursor.execute(query)
    response = cursor.fetchall()

    # convert to array of objects
    recipes = []
    for i in range(len(response)):
        temp_recipe = Recipe(response[i][0], response[i][1])
        recipes.append(temp_recipe)

    return recipes


def loadDietRecipes(dietID):
    db = dbConnect()
    cursor = db.cursor()
    query = ("SELECT diets_has_recipes.recipes_id FROM diets_has_recipes WHERE diets_id='{}';".format(dietID))
    cursor.execute(query)
    response = cursor.fetchall()

    recipes = []

    for i in range(len(response)):
        temp_recipe = loadRecipe(response[i][0])[0]    # get only recipe
        recipe = Recipe(temp_recipe.id, temp_recipe.name)
        recipes.append(recipe)

    return recipes
    """ recipe (Recipe: id, name)"""


# Diets
def loadDiet(dietID):
    db = dbConnect()
    cursor = db.cursor()

    query = ("SELECT * FROM diets WHERE id='{}';".format(dietID))
    cursor.execute(query)
    response = cursor.fetchone()

    diet = Diet(response[0], response[1], response[2], response[3], response[4])

    return diet
    """ diet (Diet: id, name, sugar, fat, protein) """


def saveDiet(diet):             # diet as object (name, sugar, fat, protein)
    db = dbConnect()
    cursor = db.cursor()

    query = ("INSERT INTO diets(name, sugar, fat, protein) VALUES ('{}', '{}', '{}', '{}');".format(diet.name, diet.sugar, diet.fat, diet.protein))
    cursor.execute(query)

    last_id = db.insert_id()
    query = ("INSERT INTO users_has_diets(users_id, diets_id) VALUES ('{}', '{}');".format(loadUser(diet.username)[0], last_id))
    cursor.execute(query)

    db.commit()

    return last_id


def loadUserDiets(username):
    db = dbConnect()
    cursor = db.cursor()
    temp_query = ("SELECT users.id FROM users WHERE users.username = '{}';".format(username))
    cursor.execute(temp_query)
    user_id = cursor.fetchone()

    query = ("SELECT diets.id, diets.name, diets.sugar, diets.fat, diets.protein FROM diets JOIN users_has_diets ON diets.id=users_has_diets.diets_id WHERE users_has_diets.users_id= '{}' ;".format(user_id[0]))
    cursor.execute(query)
    response = cursor.fetchall()

    # convert to array of objects
    diets = []
    for i in range(len(response)):
        temp_diet = Diet(response[i][0], response[i][1], response[i][2], response[i][3], response[i][4], )
        diets.append(temp_diet)

    return diets


# Ingredients
def loadAllIngredients(username):
    db = dbConnect()
    cursor = db.cursor()

    query = ("SELECT * FROM ingredients WHERE author='{}';".format(username))
    cursor.execute(query)
    response = cursor.fetchall()

    return response


def loadIngredient(ingredientID):
    db = dbConnect()
    cursor = db.cursor()

    query = ("SELECT * FROM ingredients WHERE id='{}';".format(int(ingredientID)))
    cursor.execute(query)
    response = cursor.fetchone()

    ingredient = Ingredient(response[0], response[1], response[2], response[3], response[4])

    return ingredient


def saveIngredient(ingredient, username):  # ingredient as object (name, sugar, fat, protein)
    db = dbConnect()
    cursor = db.cursor()

    query = ("INSERT INTO ingredients(name, sugar, fat, protein, author) VALUES ('{}', '{}', '{}', '{}', '{}');".format(ingredient.name, ingredient.sugar, ingredient.fat, ingredient.protein, username))
    cursor.execute(query)
    last_id = db.insert_id()

    db.commit()

    return last_id


# Users
def saveUser(username, password_hash, firstname, lastname):
    db = dbConnect()
    cursor = db.cursor()

    query = ("INSERT INTO users(username, pwdhash, firstName, lastName) VALUES ('{}', '{}', '{}', '{}');".format(username, password_hash, firstname, lastname))
    cursor.execute(query)

    db.commit()

    return cursor.rowcount


def loadUser(username):
    db = dbConnect()
    cursor = db.cursor()

    query = ("SELECT * FROM users WHERE username='{}';".format(username))
    cursor.execute(query)

    response = cursor.fetchone()
    return response


# MAIN

@route('/')
def main():
    if getSession().get('username') is not None:
        redirect('/user')
    else:
        redirect('login')


# LOGIN
@get('/login')
def login():
    session = getSession()
    if session.get('username') is not None:
        redirect('/user')
    else:
        return template('loginForm')


@post('/login')
def do_login():
    username = request.forms.get('username')
    password = request.forms.get('password')
    if check_login(username, password):
        # return "<p>Your login information was correct.</p>"
        session = getSession()
        session['username'] = username
        session.save()
        redirect('/user')
    else:
        return False


def check_login(username, password):
    user = loadUser(username)
    if user is None:
        return False

    pwdhash = user[2]

    temp_password = password.encode('utf-8')
    password_hash = hashlib.sha256(temp_password).hexdigest()

    if password_hash == pwdhash:
        return True
    else:
        return False


@route('/logout')
def logout():
    session = getSession()
    session['username'] = None
    session.save()
    redirect('/login')


@get('/register')
def register():
    return template('registerForm', username="", firstname="", lastname="", problem="")


@post('/register')
def do_register():
    username = request.forms.get('username')
    # check uniquness of username
    if loadUser(username) is not None:
        return "Uživatelské jméno nelze použít"

    temp_password = str(request.forms.get('password')).encode('utf-8')
    temp_password_2 = str(request.forms.get('againPassword')).encode('utf-8')

    password_hash = hashlib.sha256(temp_password).hexdigest()
    firstname = request.forms.get('firstname')

    lastname = request.forms.get('lastname')

    problem = ""

    if temp_password_2 != temp_password:
        problem = "Hesla jsou rozdílná!"
    if len(temp_password) < 8:
        problem = "Heslo je příliš krátké"
    if len(firstname) == 0:
        problem = "Jméno je příliš krátké"
    if len(lastname) == 0:
        problem = "Příjmení je příliš krátké"

    if problem != "":
        return template('registerForm', username=username, firstname=firstname, lastname=lastname, problem=problem)

    response = saveUser(username, password_hash, firstname, lastname)

    if response == 1:
        redirect('/login')
    else:
        return "Registrace neproběhla v pořádku"


@post('/registerValidate')
def validateRegister():
    username = request.forms.get('username')
    # print(username)
    # print(loadUser(username))
    if loadUser(username) is not None:
        # print("User found")
        return "False"
    else:
        # print("No user")
        return "True"

# USER PAGE


@route('/user')
def user():
    session = getSession()
    if session.get('username') is None:
        redirect('/login')
    diets = loadUserDiets(session['username'])
    return template('userPage', username=session['username'], diets=diets)


@route('/selectDietAJAX', method='POST')
def selectDietAJAX():
    session = getSession()
    if session.get('username') is None:
        redirect('/login')
    dietID = request.forms.get('selectDiet')
    recipes = loadDietRecipes(dietID)

    for i in range(len(recipes)):
        recipe = recipes[i]
        json_recipe = {'id': recipe.id, 'name': recipe.name}
        recipes[i] = json_recipe

    array_recipes = {'array': recipes, 'dietID': dietID}
    return array_recipes


# NEW DIET
@route('/newdiet')
def newDietShow():
    session = getSession()
    if session.get('username') is None:
        redirect('/login')
    return template('newDietPage')


@route('/addDietAJAX', method='POST')
def addDietAJAX():
    session = getSession()
    if session.get('username') is None:
        redirect('/login')
    diet = type('', (), {})()               # Magický trik, jak udělat prázdný objekt
    diet.name = request.forms.get("name")
    if len(diet.name) == 0:
        return "Vyplňte název"
    diet.sugar = request.forms.get("sugar")
    if len(diet.sugar) == 0:
        return "Vyplňte množství cukru"
    diet.fat = request.forms.get("fat")
    if len(diet.fat) == 0:
        return "Vyplňte množství tuku"
    diet.protein = request.forms.get("protein")
    if len(diet.protein) == 0:
        return "Vyplňte množství bílkoviny"
    diet.username = session['username']
    last_id = saveDiet(diet)
    redirect('/diet={}'.format(last_id))


# SHOW DIET PAGE
@route('/diet=<dietID>')
def showDiet(dietID):
    session = getSession()
    if session.get('username') is None:
        redirect('/login')

    diet = loadDiet(dietID)
    recipes = loadDietRecipes(diet.id)

    return template('dietPage', diet=diet, recipes=recipes)


# NEW RECIPE PAGE
@route('/newrecipe')
def newRecipe():
    session = getSession()
    if session.get('username') is None:
        redirect('/login')

    diets = loadUserDiets(session['username'])
    ingredients = loadAllIngredients(session['username'])
    temp_ingredients = []
    for ingredient in ingredients:
        temp_ingredient = Ingredient(ingredient[0], ingredient[1], ingredient[2], ingredient[3], ingredient[4])
        temp_ingredients.append(temp_ingredient)

    temp_ingredients.sort(key=lambda x: x.name)
    temp_ingredients = sorted(temp_ingredients, key=lambda x: x.name)
    return template('newRecipePage', ingredients=temp_ingredients, diets=diets)


@route('/addIngredientAJAX', method='POST')
def addIngredienttoRecipeAJAX():
    session = getSession()
    if session.get('username') is None:
        redirect('/login')
    ingredient = loadIngredient(request.forms.get("ingredient"))
    json_ingredient = {'id': ingredient.id, 'name': ingredient.name, 'sugar': ingredient.sugar, 'fat': ingredient.fat, 'protein': ingredient.protein}
    return json_ingredient


@route('/calcRecipeAJAX', method='POST')
def calcRecipeAJAX():
    session = getSession()
    if session.get('username') is None:
        redirect('/login')

    ingredients = request.forms.get("ingredientsArray")
    ingredients = [word.strip() for word in ingredients.split(',')]

    dietID = request.forms.get("recipeDiet")

    for i in range(len(ingredients)):
        ingredient = loadIngredient(ingredients[i])
        json_ingredient = {'id': ingredient.id, 'name': ingredient.name, 'sugar': ingredient.sugar, 'fat': ingredient.fat, 'protein': ingredient.protein, 'amount': ingredient.amount}
        ingredients[i] = json_ingredient

    array_ingredients = {'array': ingredients, 'dietID': dietID}
    return array_ingredients


@route('/saveRecipeAJAX', method='POST')
def addRecipeAJAX():
    session = getSession()
    if session.get('username') is None:
        redirect('/login')

    dietID = request.forms.get("selectedDietID")

    temp_ingredients = request.forms.get("ingredientsArray2")
    temp_ingredients = [word.strip() for word in temp_ingredients.split(',')]

    amounts = request.forms.get("ingredientsAmount2")
    amounts = [word.strip() for word in amounts.split(',')]

    ingredients = []
    for i in range(len(temp_ingredients)):
        ingredient = type('', (), {})()
        ingredient.id = temp_ingredients[i]
        ingredient.amount = amounts[i]
        ingredients.append(ingredient)

    recipe = type('', (), {})()
    recipe.name = request.forms.get("recipeName")

    last_id = saveRecipe(recipe, ingredients, dietID)
    redirect('/recipe=' + str(last_id))


@route('/recipe=<recipeID>')
def showRecipe(recipeID):
    recipe = loadRecipe(recipeID)[0]
    ingredientIDs = loadRecipe(recipeID)[1]
    ingredients = []
    for ID in ingredientIDs:
        ingredients.append(loadIngredient(ID))

    return template('recipePage', recipe=recipe, ingredients=ingredients)


# NEW INGREDIENT PAGE

@route('/newingredient')
def newingredient():
    session = getSession()
    if session.get('username') is None:
        redirect('/login')
    return template('newIngredientPage')


@route('/newIngredientAJAX', method='POST')
def newIngredienttoRecipeAJAX():
    session = getSession()
    if session.get('username') is None:
        redirect('/login')
    ingredient = type('', (), {})()
    ingredient.name = request.forms.get("name")
    ingredient.sugar = request.forms.get("sugar")
    ingredient.fat = request.forms.get("fat")
    ingredient.protein = request.forms.get("protein")
    saveIngredient(ingredient, session['username'])
    redirect('/newrecipe')


@route('/success')
def successPage():
    return '''
        Povedlo se! <br>
        <a href=/user>Přehled</a>
        '''
    pass

# CALCULATE RECIPE


# S'MORE
@route('/index.html')
def indexhtml():
    redirect('/')


# ERROR
@error(404)
def error404(error):
    return 'Nothing here, sorry. (Err404)'


@error(500)
def error500(error):
    return 'Something went wrong! (Err500)'


# application = bottle.default_app()
bottle.run(host='localhost', port=8080, debug=True, app=app)
