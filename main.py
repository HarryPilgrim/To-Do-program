import datetime
from datetime import date
import os.path
import sqlalchemy
from flask import Flask, jsonify, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
from sqlalchemy.sql import func
from sqlalchemy import Integer, String, Boolean, DateTime
import random
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, BooleanField, DateField
from wtforms.validators import DataRequired, URL
import csv


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_dont_share'
Bootstrap5(app)


# ---------------------------- CONNECT TO DATABASE ------------------------------- #
class Base(DeclarativeBase):
    pass

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///to-do.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)

# ---------------------------- DATABASE MODEL ------------------------------- #

class ToDo(db.Model):

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    to_do_task: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    category: Mapped[str] = mapped_column(String(250), unique=False, nullable=False)
    due_date: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


    def __repr__(self):
        """returns name of To Do when printed instead of <ToDo ID>"""
        return self.name


# ---------------------------- FLASK FORM TO CREATE NEW TASKS ------------------------------- #
class ToDoForm(FlaskForm):
    to_do_task = StringField('task', validators=[DataRequired()])
    category = SelectField('category', validators=[DataRequired()], choices=[])
    due_date = DateField('Due Date', default = datetime.datetime.today(), validators=[DataRequired()])

    submit = SubmitField('Submit')


# ---------------------------- INITIAL CREATION OF DATABASE ------------------------------- #
file_path = "/instance/to-do.db"
if not os.path.exists(file_path):
##to initially create database
    with app.app_context():
        db.create_all()



# ---------------------------- FLASK WEBPAGES  ------------------------------- #

@app.route("/<ordering_by>", methods=["GET", "POST"])
def main_page(ordering_by):
    if ordering_by == 'due_date':
        all_database_entries = db.session.execute(db.select(ToDo).order_by(ToDo.due_date)).scalars()
    elif ordering_by == 'category':
        all_database_entries = db.session.execute(db.select(ToDo).order_by(ToDo.category)).scalars()


    form = ToDoForm()
    form.category.choices = [("add_new_category", "add new category")] + list(set([(to_do.category, to_do.category) for to_do in ToDo.query.all()]))
 ####should remove duplicates
    if form.validate_on_submit():


        new_todo = ToDo(
            # to_do_task = request.form.get("to_do_task"),
            # category = request.form.get("category"),
            # due_date = request.form.get("due_date"),
            to_do_task = form.to_do_task.data,
            category = form.category.data,
            due_date = form.due_date.data,

        )
        db.session.add(new_todo)
        db.session.commit()

        if form.category.data == "add_new_category":
            return redirect(url_for('add_category'), code=302)


        else:
            return redirect(url_for('main_page'), code=302)

        # if formy.category.choices == "add_new_category":
        #     if request.method == "GET":
        #         return redirect("add-category.html")
        #     elif request.method == "POST":
        #         new_category = request.form.get("fname")
        #         print(new_category)


    return render_template("index.html", form=form, database_entries=all_database_entries)


@app.route("/add-category", methods=["GET", "POST"])
def add_category():

    cat_to_change = db.session.execute(db.select(ToDo).where(ToDo.category == "add_new_category")).scalar()
    task_name = cat_to_change.to_do_task

    if request.method == "GET":
        return render_template("add-category.html", task_name=task_name)
    elif request.method == "POST":
        new_category = request.form.get("fname")
        cat_to_change.category = new_category
        db.session.commit()

        return redirect(url_for('main_page'))


@app.route("/order-by-date")
def order_by_date():
    db.session.execute(db.select(ToDo).order_by(ToDo.due_date))
    db.session.commit()
    return redirect(url_for('main_page'))

@app.route("/order-by-cat")
def order_by_cat():
    db.session.execute(db.select(ToDo).order_by(ToDo.category))
    db.session.commit()
    return redirect(url_for('main_page'))


@app.route("/delete-to-do/<int:to_do_id>")
def delete_todo(to_do_id):
    task_to_delete = db.session.execute(db.select(ToDo).where(ToDo.id == to_do_id)).scalar()
    db.session.delete(task_to_delete)
    db.session.commit()
    return redirect(url_for('main_page'))

@app.route("/edit-to-do/<int:to_do_id>", methods=["GET", "POST"])
def edit_todo(to_do_id):
    todo_to_edit = db.session.execute(db.select(ToDo).where(ToDo.id == to_do_id)).scalar()
    if request.method == "GET":
        return render_template("edit-todo.html", todo_to_edit=todo_to_edit)
    elif request.method == "POST":


        try:
            task = request.form.get("task")
            todo_to_edit.to_do_task = task
        except TypeError:
            pass

        try:
            cat = request.form.get("cat")
            todo_to_edit.category = cat
        except TypeError:
            pass

        try:
            date = request.form.get("date")
            #print(date)
            #print(type(date))
            int_year = int(date[0:4])
            int_month = int(date[5:7])
            int_day = int(date[8:10])    #####turning html date into a python datetime object
            #print(str_year)
            #print(str_month)
            #print(str_day)
            real_date = datetime.datetime(int_year, int_month, int_day, 1,1)
            print(real_date)
            print(type(real_date))
            todo_to_edit.due_date = real_date
        except TypeError:
            pass
        except sqlalchemy.exc.StatementError:
            pass



        # if request.form.get("task") == None:
        #     pass
        # else:
        #     task = request.form.get("task")
        #     print(task)
        #     todo_to_edit.to_do_task = task
        #
        # if request.form.get("cat") == None:
        #     pass
        # else:
        #     cat = request.form.get("cat")
        #     todo_to_edit.category = cat
        #
        # if request.form.get("date") == None:
        #     pass
        # else:
        #     date = request.form.get("date")
        #     todo_to_edit.due_date = date
        db.session.commit()

        return redirect(url_for('main_page'))




if __name__ == "__main__":
    app.run(debug=True)