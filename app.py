

from flask import Flask, flash, request, redirect, url_for, render_template, make_response
from packages.OwlQuery import OwlQuery
import os

owl_path = os.environ.get("OWL_PATH")

app = Flask(__name__)

owl = OwlQuery(owl_path)


@app.route('/')
def home():
    return render_template("index.html", process=owl.get_process())


@app.route('/get_itp', methods=['POST'])
def get_inputs_tools_outputs():

    process_name = request.form.get("process_name", "")

    datas = owl.data(process_name)

    return make_response(render_template('show_ito.html', data=datas[process_name], process_name=process_name))


if __name__ == '__main__':
    app.run()
