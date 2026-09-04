import streamlit as st
import sqlite3
import pandas as pd
from pathlib import Path

st.set_page_config(
    page_title="Meus Vinhos",
    page_icon="🍷",
    layout="wide"
)

BANCO = Path(__file__).resolve().parent / "vinhos.db"

st.markdown("""
<style>
    .block-container {
        padding-top: 2rem;
        padding-left: 4rem;
        padding-right: 4rem;
    }

    .titulo {
        font-size: 35px;
        font-weight: 600;
        letter-spacing: -1px;
        margin-bottom: 0;
    }

    .subtitulo {
        font-size: 18px;
        margin-bottom: 35px;
        opacity: 0.65;
    }

    .secao {
        font-size: 28px;
        font-weight: 600;
        margin-top: 35px;
        margin-bottom: 20px;
    }

    .card {
        border: 1px solid rgba(128,128,128,0.25);
        border-radius: 16px;
        padding: 22px;
        min-height: 250px;
        margin-bottom: 20px;
    }

    .card-titulo {
        font-size: 21px;
        font-weight: 600;
        margin-bottom: 8px;
    }

    .card-info {
        font-size: 15px;
        opacity: 0.7;
        margin-bottom: 5px;
    }

    .nota {
        font-size: 18px;
        margin-top: 15px;
    }

    .hero {
        border-radius: 20px;
        padding: 25px;
        margin-bottom: 40px;
        background: linear-gradient(
            135deg,
            rgba(120,80,50,0.18),
            rgba(180,150,100,0.08)
        );
    }

    .hero-titulo {
        font-size: 36px;
        font-weight: 600;
    }

    .hero-texto {
        font-size: 18px;
        opacity: 0.7;
    }

    div[data-testid="stMetric"] {
        border: 1px solid rgba(128,128,128,0.2);
        padding: 20px;
        border-radius: 14px;
    }
</style>
""", unsafe_allow_html=True)


def conectar():
    return sqlite3.connect(BANCO)


conexao = conectar()

conn = conectar()

df_vinhos = pd.read_sql_query("""
    SELECT
        id,
        nome,
        vinicola,
        pais,
        regiao,
        uva,
        safra,
        tipo,
        nota,
        nota_vivino
    FROM vinhos
    ORDER BY id DESC
""", conexao)

df_vinicolas = pd.read_sql_query("""
     SELECT
            id as vinicola_id,
            nome,
            pais,
            regiao,
            subregiao,
            cidade,
            site,
            instagram,
            visitada,
            descricao
        FROM vinicolas
        ORDER BY nome ASC
""", conexao)

conexao.close()


st.markdown(
    '<div class="titulo">🍷 Meus Vinhos</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitulo">Minha coleção pessoal de vinhos</div>',
    unsafe_allow_html=True
)

if "menu" not in st.session_state:
    st.session_state["menu"] = "Início"

menu = st.radio(
    "",
    [
        "Início",
        "Meus Vinhos",
        "Vinícolas",
        "Regiões",
        "OCR"
    ],
    horizontal=True
)


st.divider()


if menu == "Início":

    st.markdown("""
    <div class="hero">
        <div class="hero-titulo">Minha coleção</div>
        <div class="hero-texto">
            Um catálogo pessoal para registrar, organizar e descobrir meus vinhos.
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "🍷 Vinhos",
            len(df_vinhos)
        )

    with col2:
        st.metric(
            "🏛️ Vinícolas",
            len(df_vinicolas)
        )

    with col3:
        if len(df_vinicolas) > 0:
            paises = df_vinicolas["pais"].dropna().nunique()
        else:
            paises = 0

        st.metric(
            "🌎 Países",
            paises
        )

    with col4:
        if len(df_vinhos) > 0 and df_vinhos["nota_vivino"].notna().any():
            nota_media = df_vinhos["nota_vivino"].mean()
            st.metric(
                "⭐ Nota média",
                f"{nota_media:.1f}"
            )
        else:
            st.metric(
                "⭐ Nota média",
                "-"
            )


    st.markdown(
        '<div class="secao">Últimos vinhos</div>',
        unsafe_allow_html=True
    )

    if len(df_vinhos) == 0:

        st.info("Nenhum vinho cadastrado ainda.")

    else:

        ultimos = df_vinhos.head(6)

        colunas = st.columns(3)

        for i, (_, vinho) in enumerate(ultimos.iterrows()):

            with colunas[i % 3]:

                nome = vinho["nome"] or "Vinho sem nome"
                vinicola = vinho["vinicola"] or "Vinícola não informada"
                pais = vinho["pais"] or "País não informado"
                uva = vinho["uva"] or "Uva não informada"

                if pd.notna(vinho["nota_vivino"]):
                    nota = f"⭐ {vinho['nota_vivino']}"
                else:
                    nota = "⭐ Sem nota"

                st.markdown(f"""
                <div class="card">

                    <div style="
                        height:100px;
                        display:flex;
                        align-items:center;
                        justify-content:center;
                        font-size:55px;
                        opacity:0.65;
                    ">
                        🍷
                    </div>

                    <div class="card-titulo">
                        {nome}
                    </div>

                    <div class="card-info">
                        {vinicola}
                    </div>

                    <div class="card-info">
                        {uva} · {pais}
                    </div>

                    <div class="nota">
                        {nota}
                    </div>

                </div>
                """, unsafe_allow_html=True)


elif menu == "Meus Vinhos":

    st.markdown(
        '<div class="secao">🍷 Minha coleção</div>',
        unsafe_allow_html=True
    )

    pesquisa = st.text_input(
        "🔎 Pesquisar vinho",
        placeholder="Digite o nome, vinícola, uva ou país..."
    )

    df_filtrado = df_vinhos.copy()

    if pesquisa:

        termo = pesquisa.lower()

        df_filtrado = df_filtrado[
            df_filtrado.astype(str)
            .apply(
                lambda coluna: coluna.str.lower().str.contains(
                    termo,
                    na=False
                )
            )
            .any(axis=1)
        ]

    if len(df_filtrado) == 0:

        st.info("Nenhum vinho encontrado.")

    else:

        colunas = st.columns(3)

        for i, (_, vinho) in enumerate(df_filtrado.iterrows()):

            with colunas[i % 3]:

                nome = vinho["nome"] or "Vinho sem nome"
                vinicola = vinho["vinicola"] or "Vinícola não informada"
                pais = vinho["pais"] or "-"
                regiao = vinho["regiao"] or "-"
                uva = vinho["uva"] or "-"
                safra = vinho["safra"] if pd.notna(vinho["safra"]) else "-"
                nota = vinho["nota_vivino"] if pd.notna(vinho["nota_vivino"]) else "-"

                st.markdown(f"""
                <div class="card">

                    <div style="
                        height:110px;
                        display:flex;
                        align-items:center;
                        justify-content:center;
                        font-size:60px;
                    ">
                        🍷
                    </div>

                    <div class="card-titulo">
                        {nome}
                    </div>

                    <div class="card-info">
                        🏛️ {vinicola}
                    </div>

                    <div class="card-info">
                        🍇 {uva}
                    </div>

                    <div class="card-info">
                        🌎 {pais} · {regiao}
                    </div>

                    <div class="card-info">
                        📅 Safra: {safra}
                    </div>

                    <div class="nota">
                        ⭐ {nota}
                    </div>

                </div>
                """, unsafe_allow_html=True)


elif menu == "Vinícolas":

    st.markdown(
        '<div class="secao">🏛️ Vinícolas e Produtores</div>',
        unsafe_allow_html=True
    )

    regiao_selecionada = st.session_state.get(
        "regiao_selecionada"
    )

    conexao = conectar()

    if regiao_selecionada:

        st.markdown(
            f"### 🌎  {regiao_selecionada}"
        )

        df_vinicolas = pd.read_sql_query(
            """
            SELECT
                id AS vinicola_id,
                nome,
                regiao,
                subregiao,
                pais,
                visitada,
                instagram
            FROM vinicolas
            WHERE regiao = ?
            ORDER BY nome ASC
            """,
            conexao,
            params=(regiao_selecionada,)
        )

    else:

        st.markdown("### 🌎 Todas as regiões")

        pesquisa_vinicola = st.text_input(
            "🔎 Pesquisar vinícolas",
            placeholder="Digite o nome da vinícola ou produtor..."
        )

        df_filtrado_vinicola = df_vinicolas.copy()
        
        if pesquisa_vinicola.strip() != "":
        
            termo_vinicola = pesquisa_vinicola.lower()
        
            df_filtrado_vinicola = df_filtrado_vinicola[
                df_filtrado_vinicola.astype(str)
                .apply(
                    lambda coluna: coluna.str.lower().str.contains(
                        termo_vinicola,
                        na=False
                    )
                )
                .any(axis=1)
            ]
   
            if len(df_filtrado_vinicola) == 0:
            
                st.info("Nenhuma vinícola encontrada.")
            
            else:

                st.info(f"Encontrei {len(df_filtrado_vinicola)} vinícola(s) na pesquisa.")


        df_vinicolas = df_filtrado_vinicola[
                [
                    "vinicola_id",
                    "nome",
                    "regiao",
                    "subregiao",
                    "pais",
                    "visitada",
                    "instagram"
                ]
            ]
            

    if len(df_vinicolas) == 0 and len(pesquisa_vinicola.strip()) == 0:

        st.info("Nenhuma vinícola cadastrada.")

    else:

        st.caption(
            "Vinícolas e Produtores cadastrados com a ajuda da API do IA Gemini."
        )

        df_editado = st.data_editor(
            df_vinicolas,
            column_config={
                "vinicola_id": None,
                "nome": "Nome",
                "regiao": "Região",
                "subregiao": "Sub-região",
                "pais": "País",
                "instagram": st.column_config.LinkColumn(
                        "Instagram",
                        ),
                "visitada": st.column_config.CheckboxColumn(
                        "Visitada",
                        help="Marcação das vinícolas já visitadas",
                        default=False
                    )   
            },
            disabled=[
                "vinicola_id",
                "nome",
                "regiao",
                "subregiao",
                "pais",
                "instagram"            
            ],
            hide_index=True,
            use_container_width=True
        )

    if st.button("💾 Salvar alterações", key="salvar_vinicolas"):

        cursor = conn.cursor()

        for _, linha in df_editado.iterrows():

            cursor.execute(
                """
                UPDATE vinicolas
                SET visitada = ?
                WHERE id = ?
                """,
                (
                    linha["visitada"],
                    linha["vinicola_id"]
                )
            )

        conn.commit()

        st.success("Alterações salvas!")


    if regiao_selecionada:

        st.info(
            f"Você está visualizando somente as vinícolas desta região. "
           #f"**{regiao_selecionada}**."
        )

        if st.button("← Ver TODAS as Vinícolas e Produtores", key="ver_todas_vinicolas"):
            st.session_state["regiao_selecionada"] = None
            st.rerun()

elif menu == "Regiões":

    from pathlib import Path

    st.markdown(
        '<div class="secao">🌎 Regiões</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        "Explore sua coleção de vinhos pelas regiões produtoras."
    )

    # =========================================================
    # PASTA DAS IMAGENS
    # =========================================================

    PASTA_REGIOES = (
        Path(__file__).resolve().parent
        / "imagens_regioes"
    )

    # =========================================================
    # IMAGENS
    # =========================================================

    imagens_regioes = {
        "Mendoza": "mendoza.jpg",
        "Alentejo": "alentejo.jpg",
        "Montevidéu": "montevideu.jpg",
        "Serra Gaúcha": "serragaucha.jpg",
        "Douro": "douro.jpg",
        "Salta": "salta.jpg",
        "Serra Catarinense": "serracatarinense.jpg",
        "Valle del Maipo": "valledelmaipo.jpg"
    }


    # =========================================================
    # CONSULTAR BANCO
    # =========================================================

    conexao = conectar()

    df_regioes = pd.read_sql_query(
        """
        SELECT
            regiao,
            pais,
            COUNT(*) AS quantidade_vinicolas
        FROM vinicolas
        WHERE regiao IS NOT NULL
          AND TRIM(regiao) <> ''
        GROUP BY regiao, pais
        ORDER BY quantidade_vinicolas DESC
        """,
        conexao
    )

    conexao.close()

    # =========================================================
    # EXIBIR REGIÕES
    # =========================================================

    if df_regioes.empty:

        st.info("Nenhuma região encontrada.")

    else:

        colunas = st.columns(3)

        for i, (_, linha) in enumerate(
            df_regioes.iterrows()
        ):

            nome_regiao = str(linha["regiao"])

            nome_arquivo = imagens_regioes.get(nome_regiao)

            if nome_arquivo:
                caminho_imagem = PASTA_REGIOES / nome_arquivo
            else:
                caminho_imagem = None

            pais = (
                str(linha["pais"])
                if linha["pais"]
                else "País não informado"
            )

            quantidade_vinicolas = int(
                linha["quantidade_vinicolas"]
            )

            caminho_imagem = (
                PASTA_REGIOES
                / imagens_regioes.get(
                    nome_regiao,
                    ""
                )
            )

            with colunas[i % 3]:

                # =================================================
                # IMAGEM
                # =================================================

                if caminho_imagem is not None and caminho_imagem.is_file():

                     st.image(
                         str(caminho_imagem),
                         use_container_width=True
                      )

                else:

                    st.info(
                        f"Imagem não encontrada para {nome_regiao}"
                    )

                # =================================================
                # INFORMAÇÕES
                # =================================================

                st.markdown(
                    f"### {nome_regiao}"
                )

                st.caption(
                    f" {pais}"
                )

                col1, col2 = st.columns(2)

                with col1:

                    st.metric(
                        "🏛️ Vinícolas",
                        quantidade_vinicolas
                    )

                with col2:

                    st.metric(
                        "🍷 Vinhos",
                        "—"
                    )

                # =================================================
                # BOTÃO
                # =================================================

                if st.button(
                    "🍷 Explorar região",
                    key=f"explorar_regiao_{i}",
                    use_container_width=True
                ):

                    st.session_state["regiao_selecionada"] = nome_regiao
                    st.session_state["menu"] = "Vinícolas"

                    st.rerun()

                st.divider()

elif menu == "OCR":

    st.markdown(
        '<div class="secao">📷 Leitura OCR dos vinhos</div>',
        unsafe_allow_html=True
    )

    conexao = conectar()

    df_ocr = pd.read_sql_query("""
        SELECT
            id AS ocr_id,
            foto_arquivo,
            foto_data,
            foto_fabricante,
            foto_modelo,
            foto_software,
            ocr_texto,
            vinho_tavily,
            vinho
        FROM ocr_vinhos
        ORDER BY foto_arquivo DESC
    """, conexao)

    conexao.close()

    if len(df_ocr) == 0:

        st.info("Nenhum OCR cadastrado.")

    else:

        st.markdown(
            "### ✏️ Exibir as informações do OCR"
        )

        st.caption(
            "Nesta etapa vamos preparar o nome do vinho para a pesquisa no Gemini."
        )

        df_editado = st.data_editor(
            df_ocr,
            column_config={
                "ocr_id": "OCR",
                "foto_arquivo": "Arquivo",
                "foto_data": "Data da foto",
                "foto_fabricante": "Fabricante",
                "foto_modelo": "Modelo",
                "foto_software": "Software",
                "ocr_texto": "Texto OCR",
                "vinho_tavily": "Vinho Tavily",
                "vinho": "Vinho"               
            },
            disabled=[
                "ocr_id",
                "foto_arquivo",
                "foto_data",
                "foto_fabricante",
                "foto_modelo",
                "foto_software",
                "ocr_texto",
                "vinho_tavily"
            ],
            hide_index=True,
            use_container_width=True
        )

    if st.button("💾 Salvar alterações", key="salvar_ocr_vinhos"):

        cursor = conn.cursor()

        for _, linha in df_editado.iterrows():

            cursor.execute(
                """
                UPDATE ocr_vinhos
                SET vinho = ?
                WHERE id = ?
                """,
                (
                    linha["vinho"],
                    linha["ocr_id"]
                )
            )

        conn.commit()

        st.success("Alterações salvas!")

    st.info(
            "A próxima etapa será deixar a coluna \"Vinho\" como uma coluna editável "
        )