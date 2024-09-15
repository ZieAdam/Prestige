from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configuration de la base de données
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///candidats.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modèle pour stocker les candidats et les scores
class Candidat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    critere1 = db.Column(db.Integer, nullable=False)
    critere2 = db.Column(db.Integer, nullable=False)
    critere3 = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return "<Candidat {}>".format(self.nom)

# Route pour la page d'accueil
@app.route('/')
def index():
    candidats = Candidat.query.all()
    return render_template('index.html', candidats=candidats)

# Route pour ajouter un candidat
@app.route('/ajouter', methods=['POST'])
def ajouter_candidat():
    nom = request.form['nom']
    critere1 = int(request.form['critere1'])
    critere2 = int(request.form['critere2'])
    critere3 = int(request.form['critere3'])
    
    nouveau_candidat = Candidat(nom=nom, critere1=critere1, critere2=critere2, critere3=critere3)
    db.session.add(nouveau_candidat)
    db.session.commit()
    
    return redirect(url_for('index'))

# Route pour afficher les résultats
@app.route('/resultats')
def resultats():
    candidats = Candidat.query.all()
    # Calcul du score total pour chaque candidat
    for candidat in candidats:
        candidat.score_total = candidat.critere1 + candidat.critere2 + candidat.critere3
    # Trier les candidats par score total décroissant
    candidats = sorted(candidats, key=lambda x: x.score_total, reverse=True)
    
    return render_template('resultats.html', candidats=candidats)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)