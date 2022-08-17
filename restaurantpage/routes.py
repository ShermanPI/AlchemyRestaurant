import os
import secrets
from PIL import Image 
from flask import jsonify, render_template, flash, redirect, url_for, request
from restaurantpage import app, db, bcrypt
from restaurantpage.forms import RegistrationForm, LoginForm, UpdataeAccountForm, AddRestaurantForm, AddMenuItem, UpdateRestaurantForm, FilterForm
from datetime import datetime
from restaurantpage.models import User, Restaurant, MenuItem
from flask_login import login_user, current_user, logout_user, login_required

@app.route('/', methods=['GET', 'POST'])
def home():
    restaurants = Restaurant.query.all()

    fast_food_restaurants = []
    bakery_restaurants = []
    casual_restaurants = []
    sea_food_restaurants = []
    filter_ready = False

    form = FilterForm()

    if form.validate_on_submit():
        filter_ready = True
        searchFilter = f"%{form.name.data}%"
        print(searchFilter)
        restaurants = Restaurant.query.filter(Restaurant.name.ilike(searchFilter)).all()

        if not restaurants:
            flash('No restaurants matching this information', category='danger')
            return redirect(url_for('home'))

    for restaurant in restaurants:
        if restaurant.type == 'Fast food':
            fast_food_restaurants.append(restaurant)
        elif restaurant.type == 'Bakery':
            bakery_restaurants.append(restaurant)
        elif restaurant.type == 'Casual':
            casual_restaurants.append(restaurant)
        elif restaurant.type == 'Sea Food':
            sea_food_restaurants.append(restaurant)

    total_restaurants = [len(bakery_restaurants), len(fast_food_restaurants), len(sea_food_restaurants), len(casual_restaurants)]

    return render_template('index.html', title = " - Home", form = form,fast_food_restaurants = fast_food_restaurants, bakery_restaurants = bakery_restaurants, casual_restaurants = casual_restaurants, sea_food_restaurants = sea_food_restaurants, total_restaurants = total_restaurants, filter_ready = filter_ready)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = RegistrationForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-')
        user = User(username = form.username.data, email = form.email.data, password = hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f"Your account has been successfully created! Now you can Log In", 'success')
        return redirect(url_for('login'))

    return render_template('register.html', title = ' - Register',form = form)

@app.route('/login',  methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()

        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember= form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash(f"There is no account matching the information, check email and password", 'danger')
            
    return render_template('login.html', title = ' - Log In', form = form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/<int:account_id>/account')
@login_required
def account(account_id):
    user = User.query.filter_by(id = account_id).first()
    image_file = url_for('static', filename = 'img/profile/' + user.image_file)

    return render_template('account.html', title = " - My Account", image_file = image_file, user = user)

@app.route('/<int:restaurant_id>/add_item', methods=['GET', 'POST'])
@login_required
def addItem(restaurant_id):
    form = AddMenuItem()
    restaurant = Restaurant.query.filter_by(id = restaurant_id).first()
     
    if current_user.id == restaurant.owner.id:

        if form.validate_on_submit():
            prev_picture = os.path.join(app.root_path, 'static/img/item', current_user.image_file)
            if os.path.exists(prev_picture):
                os.remove(prev_picture)

            picture_file = save_picture(form.image_file.data, 'static/img/item')
            newItem = MenuItem(name = form.name.data, image_file = picture_file, course = form.type.data, description = form.description.data, price = form.price.data, restaurant_id = restaurant.id)
            db.session.add(newItem)
            db.session.commit()

            flash('The item has been successfully added', 'success')
            return redirect(url_for('addItem', restaurant_id = restaurant_id))

        return render_template('add_menuItem.html', title = " - Add New Item", form = form, restaurant = restaurant)

    else:
        flash('You need to be the owner of this restaurant to be able to edit this information', 'danger')
        return redirect(url_for('menu', restaurant_id = restaurant_id))

@app.route('/<int:restaurant_id>/menu')
def menu(restaurant_id):
    restaurant = Restaurant.query.filter_by(id = restaurant_id).first()
    entreeMenuItems = MenuItem.query.filter_by(restaurant_id = restaurant_id, course = 'Entree').all()
    dessertMenuItems = MenuItem.query.filter_by(restaurant_id = restaurant_id, course = 'Dessert').all()
    appetizerMenuItems = MenuItem.query.filter_by(restaurant_id = restaurant_id, course = 'Appetizer').all()


    return render_template('menu.html', title = f" - {restaurant.name} menu", restaurant = restaurant, entreeMenuItems = entreeMenuItems, dessertMenuItems = dessertMenuItems, appetizerMenuItems = appetizerMenuItems)


def save_picture(form_picture, path):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    pic_filename = random_hex + f_ext
    picture_path = os.path.join(app.root_path, path, pic_filename)
    
    output_size = (350, 350)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    
    i.save(picture_path) #the form.image_file.data also have a save function like Image class
    return pic_filename

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = UpdataeAccountForm()

    if form.validate_on_submit():
        if form.image_file.data:
            prev_picture = os.path.join(app.root_path, 'static/img/profile', current_user.image_file)
            if os.path.exists(prev_picture) and current_user.image_file != 'user.png':
                os.remove(prev_picture)

            picture_file = save_picture(form.image_file.data, 'static/img/profile')
            current_user.image_file = picture_file

        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated', 'success')
        return redirect(url_for('account', account_id = current_user.id))
        
    elif request.method == 'GET':
        form.email.data = current_user.email
        form.username.data = current_user.username
    
    return render_template('edit_profile.html', title = " - Edit Profile", form = form)

#change this, putting an atributte folder


@app.route('/add_restaurant', methods=['GET', 'POST'])
@login_required
def add_restaurant():
    form = AddRestaurantForm()
    if form.validate_on_submit():

        prev_picture = os.path.join(app.root_path, 'static/img/restaurant_image', current_user.image_file)
        if os.path.exists(prev_picture):
            os.remove(prev_picture)

        picture_file = save_picture(form.image_file.data, 'static/img/restaurant_image')
        restaurant = Restaurant(name = form.name.data, image_file = picture_file, type = form.type.data, user_id = current_user.id)
        db.session.add(restaurant)
        db.session.commit()

        flash("Your restaurant has been added to Alchemist Restaurants", "success")
        return redirect(url_for('home'))

    return render_template('add_restaurant.html',  title = " - Add Restaurant", form = form)

@app.route('/<int:restaurant_id>/edit_restaurant', methods=['GET', 'POST'])
@login_required
def edit_restaurant(restaurant_id):
    
    restaurant = Restaurant.query.filter_by(id = restaurant_id).first()
    form = UpdateRestaurantForm()
    form.setRestaurantToEdit(restaurant)

    if current_user.id == restaurant.owner.id:
        if form.validate_on_submit():
              
            if form.image_file.data:
                prev_picture = os.path.join(app.root_path, 'static/img/restaurant_image', current_user.image_file)
                if os.path.exists(prev_picture):
                    os.remove(prev_picture)

                picture_file = save_picture(form.image_file.data, 'static/img/restaurant_image')
                restaurant.image_file = picture_file
            
            restaurant.name = form.name.data
            restaurant.type = form.type.data

            db.session.commit()
            flash('The information has been updated', 'success')
            return redirect(url_for('menu', restaurant_id = restaurant.id))

        elif request.method == 'GET':
            form.name.data = restaurant.name
            form.type.data = restaurant.type

        return render_template('edit_restaurant.html',  title = " - Edit Restaurant", form = form, restaurant = restaurant)
    else:
        flash('You need to be the owner of this restaurant to be able to edit this information', 'danger')
        return redirect(url_for('menu', restaurant_id = restaurant_id))


@app.route('/<int:restaurant_id>/delete_restaurant', methods=['GET', 'POST'])
@login_required
def delete_restaurant(restaurant_id):
    restaurant = Restaurant.query.filter_by(id = restaurant_id).first()
    if current_user.id == restaurant.owner.id:
        db.session.delete(restaurant)
        db.session.commit()
        flash('Restaurant has been deleted!', 'success')
        return redirect(url_for('home'))
    else:
        flash('You need to be the owner of this restaurant to be able to do this action', 'danger')
        return redirect(url_for('menu', restaurant_id = restaurant_id))

@app.route('/<int:restaurant_id>/<int:item_id>/edit_menu_item', methods=['GET', 'POST'])
@login_required
def edit_menu_item(restaurant_id, item_id):
    restaurant = Restaurant.query.filter_by(id = restaurant_id).first()
    menuItem = MenuItem.query.filter_by(id = item_id).first()

    form = AddMenuItem()

    if current_user.id == restaurant.owner.id:
        if request.method == 'POST':
            if form.validate_on_submit():
                menuItem.name = form.name.data
                menuItem.course = form.type.data
                menuItem.description   = form.description.data               
                menuItem.price = form.price.data

                if form.image_file.data:
                    prev_picture = os.path.join(app.root_path, 'static/img/item', current_user.image_file)
                    if os.path.exists(prev_picture):
                        os.remove(prev_picture)
                        
                    picture_file = save_picture(form.image_file.data, 'static/img/item')
                    menuItem.image_file = picture_file

                db.session.commit()
                flash('Changes has been applied', 'success')

                return redirect(url_for('menu', restaurant_id = restaurant.id))

        elif request.method == 'GET':
            form.name.data = menuItem.name
            form.type.data = menuItem.course
            form.description.data = menuItem.description
            form.price.data = float(menuItem.price)

        return render_template('edit_item.html', title = ' - Edit Menu Item', restaurant = restaurant, menuItem = menuItem, form = form)

    else:
        flash('You need to be the owner of this restaurant to be able to do this action', 'danger')
        return redirect(url_for('menu', restaurant_id = restaurant_id))

@app.route('/<int:restaurant_id>/<int:item_id>/delete_menu_item', methods=['GET', 'POST'])
@login_required
def delete_menu_item(restaurant_id, item_id):
    restaurant = Restaurant.query.filter_by(id = restaurant_id).first()
    menuItem = MenuItem.query.filter_by(id = item_id).first()

    form = AddMenuItem()

    if current_user.id == restaurant.owner.id:
        db.session.delete(menuItem)
        db.session.commit()
        flash('Changes has been applied!', 'success')
        return redirect(url_for('menu', restaurant_id = restaurant.id))
    else:
        flash('You need to be the owner of this restaurant to be able to do this action', 'danger')
        return redirect(url_for('menu', restaurant_id = restaurant_id))

@app.route('/<int:restaurant_id>/client_menu')
def client_menu(restaurant_id):
    restaurant = Restaurant.query.filter_by(id = restaurant_id).first()

    if restaurant.owner.id == current_user.id:
        entreeMenuItems = MenuItem.query.filter_by(restaurant_id = restaurant_id, course = 'Entree').all()
        dessertMenuItems = MenuItem.query.filter_by(restaurant_id = restaurant_id, course = 'Dessert').all()
        appetizerMenuItems = MenuItem.query.filter_by(restaurant_id = restaurant_id, course = 'Appetizer').all()
        return render_template('client_menu.html', title = f" - {restaurant.name} menu", restaurant = restaurant, entreeMenuItems = entreeMenuItems, dessertMenuItems = dessertMenuItems, appetizerMenuItems = appetizerMenuItems)
    else:
        return redirect(url_for('menu', restaurant_id = restaurant.id))

# "JSONIFY" the database

@app.route('/restaurants/JSON')
def restaurantsJSON():
    restaurants = Restaurant.query.all()
    return jsonify(restaurants = [restaurant.serialize for restaurant in restaurants])

@app.route('/restaurant/<int:restaurant_id>/JSON')
def restaurantJSON(restaurant_id):
    restaurant = Restaurant.query.filter_by(id = restaurant_id).first()
    return jsonify(restaurant = restaurant.serialize)

@app.route('/restaurant/<int:restaurant_id>/menuItem/JSON')
def menuItemsJSON(restaurant_id):
    menuItems = MenuItem.query.filter_by(restaurant_id = restaurant_id).all()
    return jsonify(menuItems = [item.serialize for item in menuItems])