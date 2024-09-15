from flask import Flask, render_template, redirect, request, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vote.db'
app.config['SECRET_KEY'] = 'secret_key_for_session'
db = SQLAlchemy(app)

class Candidat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False, unique=True)

class Juge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False, unique=True)
    a_vote = db.Column(db.Boolean, default=False)

class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    juge_id = db.Column(db.Integer, db.ForeignKey('juge.id'), nullable=False)
    candidat_id = db.Column(db.Integer, db.ForeignKey('candidat.id'), nullable=False)
    volonte_rejoindre_famille = db.Column(db.Integer, nullable=False)
    connaissance_famille = db.Column(db.Integer, nullable=False)
    prestation_presentation = db.Column(db.Integer, nullable=False)
    appreciation_personnelle = db.Column(db.Integer, nullable=False)

    juge = db.relationship('Juge', backref=db.backref('votes', lazy=True))
    candidat = db.relationship('Candidat', backref=db.backref('votes', lazy=True))

@app.route('/candidat', methods=['GET', 'POST'])
def candidat_inscription():
    if request.method == 'POST':
        nom = request.form['nom']
        candidat_existe = Candidat.query.filter_by(nom=nom).first()

        # Vérifier si le candidat existe déjà
        if candidat_existe:
            flash('Vous êtes déjà inscrit et ne pouvez pas vous inscrire à nouveau.', 'error')
        else:
            nouveau_candidat = Candidat(nom=nom)
            db.session.add(nouveau_candidat)
            db.session.commit()
            flash('Inscription réussie ! Vous êtes bien inscrit.', 'success')
        
        return redirect(url_for('candidat_inscription'))

    # Récupérer tous les candidats pour vérifier s'ils sont déjà inscrits
    candidats = Candidat.query.all()
    return render_template('candidat_inscription.html', candidats=candidats)

@app.route('/juge', methods=['GET', 'POST'])
def juge_inscription():
    if request.method == 'POST':
        nom = request.form['nom']
        juge = Juge.query.filter_by(nom=nom).first()

        # Si le juge existe déjà et a déjà voté
        if juge:
            if juge.a_vote:
                flash("Vous avez déjà voté et ne pouvez pas revoter.", "danger")
                return redirect(url_for('juge_inscription'))
            else:
                flash('Vous êtes déjà inscrit, veuillez procéder au vote.', 'success')
                return redirect(url_for('vote', juge_id=juge.id))
        else:
            # Créer un nouveau juge s'il n'existe pas
            new_juge = Juge(nom=nom)
            db.session.add(new_juge)
            db.session.commit()
            flash('Inscription réussie ! Veuillez voter.', 'success')
            return redirect(url_for('vote', juge_id=new_juge.id))

    return render_template('juge_inscription.html')

@app.route('/vote/<int:juge_id>', methods=['GET', 'POST'])
def vote(juge_id):
    juge = Juge.query.get(juge_id)
    candidats = Candidat.query.all()

    # Vérifier si le juge a déjà voté
    if juge.a_vote:
        flash("Vous avez déjà voté.", "danger")
        return redirect(url_for('juge_inscription'))

    if request.method == 'POST':
        # Si le juge n'a pas voté, lui permettre de voter
        for candidat in candidats:
            volonte = request.form.get(f'volonte_{candidat.id}', type=int)
            connaissance = request.form.get(f'connaissance_{candidat.id}', type=int)
            prestation = request.form.get(f'prestation_{candidat.id}', type=int)
            appreciation = request.form.get(f'appreciation_{candidat.id}', type=int)
            
            vote = Vote(
                juge_id=juge.id,
                candidat_id=candidat.id,
                volonte_rejoindre_famille=volonte,
                connaissance_famille=connaissance,
                prestation_presentation=prestation,
                appreciation_personnelle=appreciation
            )
            db.session.add(vote)

        # Marquer que le juge a voté
        juge.a_vote = True
        db.session.commit()

        flash("Merci pour votre vote !", "success")
        return redirect(url_for('juge_inscription'))

    return render_template('vote.html', candidats=candidats)

@app.route('/resultats', methods=['GET', 'POST'])
def resultats():
    if request.method == 'POST':
        mot_de_passe = request.form['mot_de_passe']

        # Vérification du mot de passe
        if mot_de_passe == 'admin_password':  # Assurez-vous que 'admin_password' correspond à votre mot de passe
            session['admin'] = True  # Active la session admin
            flash("Connexion réussie !", "success")
            return redirect(url_for('afficher_resultats'))  # Redirection vers les résultats
        else:
            flash("Mot de passe incorrect.", "danger")
            return redirect(url_for('resultats'))

    return render_template('resultats_login.html')

@app.route('/afficher_resultats')
def afficher_resultats():
    if 'admin' in session:  # Vérifie que l'utilisateur est bien connecté en tant qu'admin
        candidats = Candidat.query.all()

        resultats = []
        for candidat in candidats:
            total_votes = Vote.query.filter_by(candidat_id=candidat.id).all()
            score_total = sum(
                v.volonte_rejoindre_famille +
                v.connaissance_famille +
                v.prestation_presentation +
                v.appreciation_personnelle
                for v in total_votes
            )
            resultats.append({
                'nom': candidat.nom,
                'score_total': score_total
            })
        
        # Trier les résultats par score décroissant
        resultats = sorted(resultats, key=lambda x: x['score_total'], reverse=True)

        # Affiche la page avec les résultats
        return render_template('resultats.html', resultats=resultats)

    else:
        flash("Accès non autorisé.", "danger")
        return redirect(url_for('resultats'))
@app.route('/test_session')
def test_session():
    if 'admin' in session:
        return "Session active: vous êtes connecté en tant qu'administrateur."
    else:
        return "Session inactive: vous n'êtes pas administrateur."

@app.route('/deconnexion')
def deconnexion():
    session.pop('admin', None)
    flash("Déconnexion réussie.", "success")
    return redirect(url_for('resultats'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)  # '0.0.0.0' permet d'accéder depuis un autre appareil