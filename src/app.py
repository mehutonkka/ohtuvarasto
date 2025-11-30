from flask import Flask, render_template, request, redirect, url_for, flash
from varasto import Varasto


app = Flask(__name__)
app.secret_key = 'varasto-secret-key'


class VarastoStore:
    def __init__(self):
        self.varastot = {}
        self.id_counter = 0

    def get_next_id(self):
        self.id_counter += 1
        return self.id_counter

    def clear(self):
        self.varastot.clear()
        self.id_counter = 0


store = VarastoStore()
varastot = store.varastot


def parse_float(value, default=0.0):
    try:
        return float(value) if value else default
    except (ValueError, TypeError):
        return default


@app.route("/")
def index():
    return render_template("index.html", varastot=varastot)


@app.route("/varasto/new", methods=["GET", "POST"])
def new_varasto():
    if request.method == "POST":
        tilavuus = parse_float(request.form.get("tilavuus"), 0)
        alku_saldo = parse_float(request.form.get("alku_saldo"), 0)
        varasto_id = store.get_next_id()
        varastot[varasto_id] = {
            "varasto": Varasto(tilavuus, alku_saldo),
            "nimi": request.form.get("nimi", f"Varasto {varasto_id}")
        }
        return redirect(url_for("index"))
    return render_template("new_varasto.html")


@app.route("/varasto/<int:varasto_id>")
def view_varasto(varasto_id):
    if varasto_id not in varastot:
        return redirect(url_for("index"))
    return render_template(
        "view_varasto.html",
        varasto_id=varasto_id,
        data=varastot[varasto_id]
    )


@app.route("/varasto/<int:varasto_id>/edit", methods=["GET", "POST"])
def edit_varasto(varasto_id):
    if varasto_id not in varastot:
        return redirect(url_for("index"))
    if request.method == "POST":
        nimi = request.form.get("nimi", varastot[varasto_id]["nimi"])
        tilavuus = parse_float(request.form.get("tilavuus"), 0)
        varasto = varastot[varasto_id]["varasto"]
        saldo = varasto.saldo
        varastot[varasto_id]["nimi"] = nimi
        varastot[varasto_id]["varasto"] = Varasto(tilavuus, saldo)
        return redirect(url_for("view_varasto", varasto_id=varasto_id))
    return render_template(
        "edit_varasto.html",
        varasto_id=varasto_id,
        data=varastot[varasto_id]
    )


def flash_add_result(maara, tilaa, varasto):
    if maara > tilaa:
        varasto.lisaa_varastoon(maara)
        msg = f"Vain {tilaa} lisättiin, koska tilaa ei riittänyt {maara}:lle."
        flash(msg, "warning")
    else:
        varasto.lisaa_varastoon(maara)
        flash(f"{maara} lisättiin varastoon.", "success")


def flash_remove_result(maara, saldo, varasto):
    if maara > saldo:
        otettu = varasto.ota_varastosta(maara)
        msg = f"Vain {otettu} otettiin, koska saldoa ei riittänyt {maara}:lle."
        flash(msg, "warning")
    else:
        varasto.ota_varastosta(maara)
        flash(f"{maara} otettiin varastosta.", "success")


@app.route("/varasto/<int:varasto_id>/add", methods=["POST"])
def add_to_varasto(varasto_id):
    if varasto_id not in varastot:
        return redirect(url_for("index"))
    maara = parse_float(request.form.get("maara"), 0)
    varasto = varastot[varasto_id]["varasto"]
    flash_add_result(maara, varasto.paljonko_mahtuu(), varasto)
    return redirect(url_for("view_varasto", varasto_id=varasto_id))


@app.route("/varasto/<int:varasto_id>/remove", methods=["POST"])
def remove_from_varasto(varasto_id):
    if varasto_id not in varastot:
        return redirect(url_for("index"))
    maara = parse_float(request.form.get("maara"), 0)
    varasto = varastot[varasto_id]["varasto"]
    flash_remove_result(maara, varasto.saldo, varasto)
    return redirect(url_for("view_varasto", varasto_id=varasto_id))


@app.route("/varasto/<int:varasto_id>/delete", methods=["POST"])
def delete_varasto(varasto_id):
    if varasto_id in varastot:
        del varastot[varasto_id]
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run()
