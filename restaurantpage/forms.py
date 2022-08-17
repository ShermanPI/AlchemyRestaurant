from flask import Flask
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user 
from wtforms import StringField, PasswordField, SubmitField, BooleanField, ValidationError, SelectField, TextAreaField, DecimalField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from restaurantpage.models import User, Restaurant

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=15)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirmPassword = PasswordField('Confirm Password', validators = [DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username): #wtforms has this template for validate the fields 
        user = User.query.filter_by(username = username.data).first()
        if user:
            raise ValidationError('The username is already taken')
    
    def validate_email(self, email):
        email = User.query.filter_by(email = email.data).first()
        if email:
            raise ValidationError('The Email is already taken')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Log In')

class UpdataeAccountForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=15)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    image_file = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif'])])
    submit = SubmitField('Save Changes')

    def validate_username(self, username): #wtforms has this template for validate the fields 
        if username.data != current_user.username:
            user = User.query.filter_by(username = username.data).first()
            if user:
                raise ValidationError('The username is already taken')
        
    def validate_email(self, email):
        if email.data != current_user.email:
            email = User.query.filter_by(email = email.data).first()
            if email:
                raise ValidationError('The Email is already taken')

class AddRestaurantForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=4, max=17)])
    image_file = FileField('Restaurant Image', validators=[FileAllowed(['jpg', 'jpeg', 'png'])])
    type = SelectField('Restaurant Type', choices=['Fast food', 'Sea Food', 'Casual', 'Bakery'], coerce = str, validate_choice= True)
    submit = SubmitField('Create Restaurant')

    def validate_name(self, name): 
        restaurant = Restaurant.query.filter_by(name = name.data).first()
        if restaurant:
            raise ValidationError('The name is already taken, please choose another one')

class AddMenuItem(FlaskForm):
    name = StringField('Name', validators=[Length(min=4, max=20), DataRequired()])
    type = SelectField('Restaurant Type', choices=['Entree', 'Appetizer', 'Dessert'], coerce = str, validate_choice= True)
    description = TextAreaField('Description', validators=[Length(min=4), DataRequired()])
    price = DecimalField('Price', validators=[DataRequired()])
    image_file = FileField('Item Image', validators=[FileAllowed(['jpg', 'jpeg', 'png'])])
    submit = SubmitField('Submit')

    def validate_price(self, price): 
        if price.data < 0:
            raise ValidationError('The price must be 0 or above')



class UpdateRestaurantForm(FlaskForm):
    # def __init__(self, restaurantObj): --> thought to do it this way, but i cant caouse i can modify the father class of flaskform
    #     restaurant = restaurantObj

    def setRestaurantToEdit(self, restaurantObj):
        self.restaurantObj = restaurantObj

    name = StringField('Name', validators=[DataRequired(), Length(min=4, max=17)])
    image_file = FileField('Restaurant Image', validators=[FileAllowed(['jpg', 'jpeg', 'png'])])
    type = SelectField('Restaurant Type', choices=['Fast food', 'Sea Food', 'Casual', 'Bakery'], coerce = str, validate_choice= True)
    submit = SubmitField('Create Restaurant')

    def validate_name(self, name): 
        if name.data != self.restaurantObj.name:
            restaurant = Restaurant.query.filter_by(name = name.data).first()
            if restaurant:
                raise ValidationError('The name is already taken')

class FilterForm(FlaskForm):
    name = StringField(validators=[DataRequired()])
    submit = SubmitField('')