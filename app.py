from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask import send_file
import pandas as pd
import io
import xlsxwriter
app = Flask(__name__)
app.secret_key = 'chave_secreta'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///indicadores.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelo Indicador com todos os 28 campos
class Indicador(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10), nullable=False)
    uti = db.Column(db.String(20), nullable=False)
    enfermeiro = db.Column(db.String(50), nullable=False)
    turno = db.Column(db.String(10), nullable=False)
    admissoes = db.Column(db.Integer, default=0)
    readmissoes_24h = db.Column(db.Integer, default=0)
    obitos_24h = db.Column(db.Integer, default=0)
    obitos_maior_24h = db.Column(db.Integer, default=0)
    obitos_menor_7d = db.Column(db.Integer, default=0)
    obitos_maior_7d = db.Column(db.Integer, default=0)
    altas_ate_10h = db.Column(db.Integer, default=0)
    altas_depois_10h = db.Column(db.Integer, default=0)
    quedas = db.Column(db.Integer, default=0)
    quedas_risco = db.Column(db.Integer, default=0)
    transferencias = db.Column(db.Integer, default=0)
    pacientes_cvc = db.Column(db.Integer, default=0)
    perda_cvc = db.Column(db.Integer, default=0)
    cvc_nova = db.Column(db.Integer, default=0)
    extubacao_nao_planejada = db.Column(db.Integer, default=0)
    vm_nova = db.Column(db.Integer, default=0)
    pcte_vm = db.Column(db.Integer, default=0)
    pcte_sng_sne = db.Column(db.Integer, default=0)
    pacientes_avp = db.Column(db.Integer, default=0)
    perdas_avp = db.Column(db.Integer, default=0)
    transfusoes = db.Column(db.Integer, default=0)
    reacoes_transfusionais = db.Column(db.Integer, default=0)
    flebites = db.Column(db.Integer, default=0)
    erros_medicacao = db.Column(db.Integer, default=0)
    svd_svni = db.Column(db.Integer, default=0)
    svd_nova = db.Column(db.Integer, default=0)
    casos_novos_lpp = db.Column(db.Integer, default=0)
    pcte_risco_lpp = db.Column(db.Integer, default=0)
    rcp_nas_24h = db.Column(db.Integer, default=0)
    pcte_sem_dva = db.Column(db.Integer, default=0)
    pcte_cuidados_paliativos = db.Column(db.Integer, default=0)
    protocolo_me = db.Column(db.Integer, default=0)
    reinternacao_24h = db.Column(db.Integer, default=0)
    reinternacao_30d = db.Column(db.Integer, default=0)
    pacientes_permanencia_30d = db.Column(db.Integer, default=0)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')

        if email == 'uti@santamonica.com' and senha == 'uti1234':
            session['logged_in'] = True
            return redirect(url_for('principal'))
        else:
            flash("Login inválido!", "danger")

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/principal')
def principal():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    dados = Indicador.query.all()
    return render_template('principal.html', dados=dados)

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    dados = Indicador.query.all()
    return render_template('dashboard.html', dados=dados)

@app.route('/formulario', methods=['GET', 'POST'])
def formulario():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        novo_indicador = Indicador(**{campo: int(request.form[campo]) if request.form[campo].isdigit() else request.form[campo] for campo in request.form})
        db.session.add(novo_indicador)
        db.session.commit()
        flash("Indicador salvo com sucesso!", "success")
        return redirect(url_for('principal'))

    return render_template('formulario.html')

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    indicador = Indicador.query.get_or_404(id)
    
    if request.method == 'POST':
        for campo in request.form:
            setattr(indicador, campo, request.form[campo] if campo in ['data', 'uti', 'enfermeiro', 'turno'] else int(request.form[campo]))
        db.session.commit()
        return redirect(url_for('dashboard'))
    
    return render_template('editar.html', indicador=indicador)
@app.route('/excluir/<int:id>', methods=['POST'])
def excluir(id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    indicador = Indicador.query.get_or_404(id)  # Busca o indicador pelo ID
    db.session.delete(indicador)  # Exclui o registro
    db.session.commit()  # Salva as alterações no banco de dados

    flash("Indicador excluído com sucesso!", "success")
    return redirect(url_for('dashboard'))

@app.route('/api/indicadores')
def api_indicadores():
    dados = Indicador.query.all()
    return jsonify([{coluna.name: getattr(dado, coluna.name) for coluna in Indicador.__table__.columns} for dado in dados])
@app.route("/exportar_excel")
def exportar_excel():
    data_inicio = request.args.get("dataInicio")
    data_fim = request.args.get("dataFim")
    uti = request.args.get("uti")

    # Construir a query com filtros opcionais
    query = Indicador.query

    if data_inicio:
        query = query.filter(Indicador.data >= data_inicio)
    if data_fim:
        query = query.filter(Indicador.data <= data_fim)
    if uti:
        query = query.filter(Indicador.uti == uti)

    resultados = query.all()

    if not resultados:
        return "Nenhum dado encontrado para exportação", 404

    # Converter para DataFrame Pandas incluindo todos os campos
    data = [
        {
            "ID": item.id,
            "Data": item.data,
            "UTI": item.uti,
            "Enfermeiro": item.enfermeiro,
            "Turno": item.turno,
            "Admissões": item.admissoes,
            "Readmissões 24h": item.readmissoes_24h,
            "Óbitos 24h": item.obitos_24h,
            "Óbitos >24h": item.obitos_maior_24h,
            "Óbitos <7d": item.obitos_menor_7d,
            "Óbitos >7d": item.obitos_maior_7d,
            "Altas até 10h": item.altas_ate_10h,
            "Altas depois 10h": item.altas_depois_10h,
            "Quedas": item.quedas,
            "Quedas de Risco": item.quedas_risco,
            "Transferências": item.transferencias,
            "Pacientes com CVC": item.pacientes_cvc,
            "Perda de CVC": item.perda_cvc,
            "CVC Novo": item.cvc_nova,
            "Extubação Não Planejada": item.extubacao_nao_planejada,
            "Ventilação Mecânica Nova": item.vm_nova,
            "Pacientes em VM": item.pcte_vm,
            "Pacientes com SNG/SNE": item.pcte_sng_sne,
            "Pacientes com AVP": item.pacientes_avp,
            "Perda de AVP": item.perdas_avp,
            "Transfusões": item.transfusoes,
            "Reações Transfusionais": item.reacoes_transfusionais,
            "Flebites": item.flebites,
            "Erros de Medicação": item.erros_medicacao,
            "SVD/SVNI": item.svd_svni,
            "SVD Nova": item.svd_nova,
            "Casos Novos LPP": item.casos_novos_lpp,
            "Pacientes em Risco de LPP": item.pcte_risco_lpp,
            "RCP nas Últimas 24h": item.rcp_nas_24h,
            "Paciente sem DVA": item.pcte_sem_dva,
            "Paciente em Cuidados Paliativos": item.pcte_cuidados_paliativos,
            "Protocolo ME": item.protocolo_me,
            "Reinternação 24h": item.reinternacao_24h,
            "Reinternação 30d": item.reinternacao_30d,
            "Pacientes com Permanência >30d": item.pacientes_permanencia_30d
        }
        for item in resultados
    ]

    df = pd.DataFrame(data)

    # Criar arquivo Excel
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Indicadores UTI")
    output.seek(0)

    return send_file(output, download_name="indicadores_uti.xlsx", as_attachment=True)
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
