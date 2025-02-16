import os
import sqlite3

# Definir o caminho do banco de dados
db_path = os.path.join(os.getcwd(), 'instance', 'seu_banco_de_dados.db')  # Substitua pelo nome correto do seu banco de dados

# Excluir o banco de dados antigo se ele existir
if os.path.exists(db_path):
    os.remove(db_path)
    print("Banco de dados antigo excluído.")

# Criar um novo banco de dados
try:
    # Conectar ao banco de dados (novo banco será criado automaticamente)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Criar a tabela 'indicador'
    cursor.execute("""
        CREATE TABLE indicador (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT,
            uti TEXT,
            enfermeiro TEXT,
            turno TEXT,
            svd_nova INTEGER
        )
    """)
    
    # Confirmar a criação da tabela
    conn.commit()
    print("Novo banco de dados e tabela 'indicador' criados com sucesso.")
    
    # Fechar a conexão
    conn.close()

except Exception as e:
    print(f"Ocorreu um erro ao criar o banco de dados: {e}")
