import streamlit as st
import pandas as pd
from datetime import datetime
import pyodbc

# Configurações SQL Server
SERVER = 'DESKTOP-VMJS7KL'
DATABASE = 'CONTROLE_FINANCEIRO'
UID = 'joao_novaes'
PWD = 'Peduarte_9'

def get_connection():
    try:
        conn = pyodbc.connect(
            f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID={UID};PWD={PWD}'
        )
        return conn
    except Exception as e:
        st.error(f"Erro na conexão com o banco: {e}")
        return None

def carregar_movimentacoes():
    conn = get_connection()
    if not conn:
        return []
    try:
        query = "SELECT Data, Categoria, Subcategoria, Descricao, Valor, Tipo FROM Carteira_Diaria"
        df = pd.read_sql(query, conn)
        conn.close()
        df['Data'] = pd.to_datetime(df['Data']).dt.date
        return df.to_dict('records')
    except Exception as e:
        st.error(f"Erro ao carregar movimentações: {e}")
        return []

def inserir_movimentacao(mov):
    conn = get_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        sql = """
            INSERT INTO Carteira_Diaria (Data, Categoria, Subcategoria, Descricao, Valor, Tipo)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        cursor.execute(sql, mov["Data"], mov["Categoria"], mov["Subcategoria"], mov["Descricao"], mov["Valor"], mov["Tipo"])
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Erro ao inserir movimentação: {e}")
        return False

def atualizar_movimentacao(mov, old_data, old_descricao):
    conn = get_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        sql = """
            UPDATE Carteira_Diaria
            SET Data=?, Categoria=?, Subcategoria=?, Descricao=?, Valor=?, Tipo=?
            WHERE Data=? AND Descricao=?
        """
        cursor.execute(sql, mov["Data"], mov["Categoria"], mov["Subcategoria"], mov["Descricao"], mov["Valor"], mov["Tipo"], old_data, old_descricao)
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Erro ao atualizar movimentação: {e}")
        return False

def excluir_movimentacao(data, descricao):
    conn = get_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        sql = "DELETE FROM Carteira_Diaria WHERE Data=? AND Descricao=?"
        cursor.execute(sql, data, descricao)
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Erro ao excluir movimentação: {e}")
        return False

CATEGORIAS = {
    'Animais de estimação': ['Ração', 'Veterinário', 'Banho/Tosa', 'Brinquedos e acessórios'],
    'Contas e assinaturas': ['Celular', 'Streaming', 'Serviços de assinatura', 'Aplicativos pagos', 'Academia/Clubes'],
    'Despesas essenciais': ['Supermercado', 'Padaria', 'Feria/Hortifruti', 'Produtos de limpeza', 'Higiene pessoal'],
    'Compromissos financeiros': ['Cartão de crédito', 'Empréstimos/Financiamentos', 'Parcelamentos', 'Cheque especial'],
    'Educação': ['Mensalidade faculdade', 'Cursos', 'Material didático', 'Assinaturas educacionais'],
    'Filhos': ['Escola', 'Material escolar', 'Roupas/Calçados', 'Atividades extracurriculares', 'Brinquedos', 'Mesada'],
    'Investimentos': ['Aportes em investimentos', 'Poupança', 'Previdência privada', 'Reserva de emergência'],
    'Atividades de lazer': ['Restaurantes/Delivery', 'Atrações', 'Viagens', 'Presentes', 'Compras pessoais', 'Eventos sociais'],
    'Moradia': ['Aluguel/Financiamento', 'Condomínio', 'Luz', 'Água', 'Gás', 'Internet', 'IPTU', 'Seguro residencial', 'Manutenção/Reparos'],
    'Saúde': ['Plano de sáude', 'Medicamentos', 'Consultas médicas', 'Exames', 'Odontologia', 'Terapias'],
    'Transporte': ['Combustível', 'Transporte público', 'Estacionamento', 'Pedágios', 'Manutenção do carro', 'Seguro do carro', 'IPVA/Licenciamento'],
    'Outras': ['Doações', 'Gastos imprevistos', 'Taxas bancárias', 'Multas/Juros', 'Reembolsos a receber', 'Receita extra'],
    "Receita": ["Salário", "Adiantamento", "Bônus", 'Freelancer']
}

# Sessão
if "movimentacoes" not in st.session_state:
    st.session_state.movimentacoes = carregar_movimentacoes()
if "edit_index" not in st.session_state:
    st.session_state.edit_index = None
if "edit_old_data" not in st.session_state:
    st.session_state.edit_old_data = None
if "edit_old_descricao" not in st.session_state:
    st.session_state.edit_old_descricao = None

def form_movimentacao():
    if st.session_state.edit_index is not None:
        mov = st.session_state.movimentacoes[st.session_state.edit_index]
        categoria_default = mov["Categoria"]
        subcategoria_default = mov["Subcategoria"]
        data_default = mov["Data"]
        descricao_default = mov["Descricao"]
        valor_default = mov["Valor"]
        tipo_default = mov["Tipo"]
    else:
        categoria_default = list(CATEGORIAS.keys())[0]
        subcategoria_default = CATEGORIAS[categoria_default][0]
        data_default = datetime.today().date()
        descricao_default = ""
        valor_default = 0.0
        tipo_default = "Despesa"

    col1, col2 = st.columns(2)
    with col1:
        categoria = st.selectbox("Categoria", list(CATEGORIAS.keys()), index=list(CATEGORIAS.keys()).index(categoria_default), key="categoria_select")
    with col2:
        subcats = CATEGORIAS[categoria]
        subcat_index = subcats.index(subcategoria_default) if subcategoria_default in subcats else 0
        subcategoria = st.selectbox("Subcategoria", subcats, index=subcat_index, key="subcategoria_select")

    col3, col4 = st.columns(2)
    with col3:
        data = st.date_input("Data", value=data_default)
    with col4:
        valor = st.number_input("Valor (R$)", min_value=0.0, format="%.2f", value=valor_default)

    descricao = st.text_input("Descrição", value=descricao_default)
    tipo = st.selectbox("Tipo", ["Despesa", "Receita"], index=0 if tipo_default == "Despesa" else 1)

    if st.button("Salvar"):
        nova_mov = {
            "Data": data.strftime("%Y-%m-%d"),
            "Categoria": categoria,
            "Subcategoria": subcategoria,
            "Descricao": descricao,
            "Valor": valor,
            "Tipo": tipo
        }
        if st.session_state.edit_index is None:
            if inserir_movimentacao(nova_mov):
                st.success("Movimentação adicionada com sucesso!")
                st.session_state.movimentacoes.append(nova_mov)
        else:
            if atualizar_movimentacao(nova_mov, st.session_state.edit_old_data, st.session_state.edit_old_descricao):
                st.success("Movimentação atualizada com sucesso!")
                st.session_state.movimentacoes[st.session_state.edit_index] = nova_mov
                st.session_state.edit_index = None
                st.session_state.edit_old_data = None
                st.session_state.edit_old_descricao = None
        st.rerun()

st.title("📊 Registro Financeiro")
form_movimentacao()

st.subheader("📌 Movimentações registradas")

df = pd.DataFrame(st.session_state.movimentacoes)

# Filtros
col1, col2 = st.columns(2)
with col1:
    data_inicio = st.date_input("Data inicial", min(df["Data"]) if not df.empty else datetime.today().date())
with col2:
    data_fim = st.date_input("Data final", max(df["Data"]) if not df.empty else datetime.today().date())

categoria_filtrada = st.selectbox("Filtrar por categoria", options=["Todas"] + list(CATEGORIAS.keys()))
subcategoria_filtrada = st.selectbox("Filtrar por subcategoria", options=["Todas"] + sorted(set(df["Subcategoria"])))
tipo_filtrado = st.selectbox("Filtrar por tipo", options=["Todos", "Despesa", "Receita"])

# Aplicar filtros
df_filtrado = df[(df["Data"] >= data_inicio) & (df["Data"] <= data_fim)]
if categoria_filtrada != "Todas":
    df_filtrado = df_filtrado[df_filtrado["Categoria"] == categoria_filtrada]
if subcategoria_filtrada != "Todas":
    df_filtrado = df_filtrado[df_filtrado["Subcategoria"] == subcategoria_filtrada]
if tipo_filtrado != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Tipo"] == tipo_filtrado]

# Exibir movimentações filtradas
if not df_filtrado.empty:
    st.dataframe(df_filtrado, use_container_width=True)

    opcoes = [f"{i+1}. {mov['Data']} - {mov['Descricao']} ({mov['Valor']:.2f} R$)" for i, mov in df_filtrado.iterrows()]
    indices_df = df.index[df["Descricao"].isin(df_filtrado["Descricao"]) & (df["Data"].isin(df_filtrado["Data"]))].tolist()
    indice_selecionado = st.selectbox("Selecione uma movimentação:", options=range(len(opcoes)), format_func=lambda i: opcoes[i])

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Editar movimentação selecionada"):
            st.session_state.edit_index = indices_df[indice_selecionado]
            st.session_state.edit_old_data = df_filtrado.iloc[indice_selecionado]["Data"]
            st.session_state.edit_old_descricao = df_filtrado.iloc[indice_selecionado]["Descricao"]
            st.rerun()

    with col2:
        if st.button("Excluir movimentação selecionada"):
            mov = df_filtrado.iloc[indice_selecionado]
            if excluir_movimentacao(mov["Data"], mov["Descricao"]):
                st.success("Movimentação excluída com sucesso!")
                st.session_state.movimentacoes.pop(indices_df[indice_selecionado])
                st.rerun()
else:
    st.info("Nenhuma movimentação encontrada com os filtros aplicados.")