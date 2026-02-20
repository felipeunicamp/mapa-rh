import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import igraph as ig
import random
from io import StringIO


def criar_grafico_rede(df):
    """
    Função para criar o gráfico de rede de relacionamentos
    """
    try:
        # Verificar se as colunas necessárias existem
        colunas_necessarias = ['Entrevistado', 'Alvo', 'Gerencia']
        for coluna in colunas_necessarias:
            if coluna not in df.columns:
                st.error(f"❌ Coluna '{coluna}' não encontrada no arquivo CSV!")
                return None

        dados = df[['Entrevistado', 'Alvo']]

        # Criar lista de arestas
        edges = []
        for index, row in dados.iterrows():
            if pd.notna(row['Entrevistado']) and pd.notna(row['Alvo']):
                edges.append((row['Entrevistado'], row['Alvo']))

        if not edges:
            st.error("❌ Não foram encontradas conexões válidas no arquivo!")
            return None

        # Configurar cores para gerências
        gerencias = df['Gerencia'].unique()
        cores = ['red', 'blue', 'green', 'orange', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan']

        # Criar grafo
        g = ig.Graph.TupleList(edges, directed=False)

        # Mapear cores para gerências
        mapa_cores = {}
        for i, gerencia in enumerate(gerencias):
            mapa_cores[gerencia] = cores[i % len(cores)]

        # Preparar informações para hover
        hover_info = []
        tamanhos = []
        cores_pessoas = []

        for nome in g.vs['name']:
            # Calcular conexões
            conexoes_como_entrevistado = len(df[df['Entrevistado'] == nome])
            conexoes_como_alvo = len(df[df['Alvo'] == nome])
            total_conexoes = conexoes_como_entrevistado + conexoes_como_alvo

            # Tamanho do nó
            tamanho = 15 + (total_conexoes * 5)
            tamanhos.append(tamanho)

            # Encontrar gerência
            busca_entrevistado = df[df['Entrevistado'] == nome]
            if not busca_entrevistado.empty:
                gerencia_pessoa = busca_entrevistado['Gerencia'].iloc[0]
            else:
                busca_alvo = df[df['Alvo'] == nome]
                if not busca_alvo.empty:
                    gerencia_pessoa = busca_alvo['Gerencia'].iloc[0]
                else:
                    gerencia_pessoa = 'Sem Gerência'
                    if gerencia_pessoa not in mapa_cores:
                        mapa_cores[gerencia_pessoa] = 'black'

            cores_pessoas.append(mapa_cores[gerencia_pessoa])

            # Criar informações de hover
            hover_text = f"""
            <b>{nome}</b><br>
            Gerência: {gerencia_pessoa}<br>
            Total de Conexões: {total_conexoes}<br>
            Como Entrevistado: {conexoes_como_entrevistado}<br>
            Como Alvo: {conexoes_como_alvo}
            """
            hover_info.append(hover_text)

        # Configurar layout do grafo
        random.seed(42)
        layout = g.layout('fr')

        # Preparar coordenadas dos nós e arestas
        node_x = []
        node_y = []
        edge_x = []
        edge_y = []

        for posicao in layout:
            node_x.append(posicao[0])
            node_y.append(posicao[1])

        for edge in g.es:
            x1 = layout[edge.source][0]
            y1 = layout[edge.source][1]
            x2 = layout[edge.target][0]
            y2 = layout[edge.target][1]
            edge_x.extend([x1, x2, None])
            edge_y.extend([y1, y2, None])

        nomes = g.vs['name']

        # Criar figura
        fig = go.Figure()

        # Adicionar arestas (sem hover)
        fig.add_trace(go.Scatter(
            x=edge_x,
            y=edge_y,
            mode='lines',
            line=dict(color='gray', width=1),
            showlegend=False,
            hoverinfo='skip'
        ))

        # Adicionar nós COM hover personalizado
        fig.add_trace(go.Scatter(
            x=node_x,
            y=node_y,
            mode='markers+text',
            text=nomes,
            textposition='middle center',
            marker=dict(size=tamanhos, color=cores_pessoas),
            hovertemplate='%{customdata}<extra></extra>',
            customdata=hover_info,
            showlegend=False
        ))

        # Adicionar legenda das gerências
        for gerencia in gerencias:
            fig.add_trace(go.Scatter(
                x=[None],
                y=[None],
                mode='markers',
                marker=dict(size=15, color=mapa_cores[gerencia]),
                name=gerencia,
                showlegend=True
            ))

        # Configurar layout
        fig.update_layout(
            title={
                'text': '<b>Mapeamento de Rede de Relacionamentos</b>',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 24}
            },
            xaxis=dict(
                showgrid=False,
                zeroline=False,
                showticklabels=False,
                showline=False
            ),
            yaxis=dict(
                showgrid=False,
                zeroline=False,
                showticklabels=False,
                showline=False
            ),
            plot_bgcolor='white',
            paper_bgcolor='white',
            showlegend=True,
            legend=dict(
                font=dict(
                    size=18,
                    family="Arial",
                    color="black"
                )
            ),
            height=700
        )

        return fig

    except Exception as e:
        st.error(f"❌ Erro ao processar o arquivo: {str(e)}")
        return None


def main():
    # Configuração da página
    st.set_page_config(
        page_title="Mapeamento de Rede de Relacionamentos",
        page_icon="🕸️",
        layout="wide"
    )

    # Título principal
    st.title("🕸️ Mapeamento de Rede de Relacionamentos")
    st.markdown("---")

    # Sidebar com instruções
    with st.sidebar:
        st.header("📋 Instruções")
        st.markdown("""
        **Formato do arquivo CSV:**

        O arquivo deve conter as seguintes colunas:
        - `Entrevistado`: Nome da pessoa que fez a indicação
        - `Alvo`: Nome da pessoa indicada
        - `Gerencia`: Gerência da pessoa

        **Exemplo:**
        ```
        Entrevistado,Alvo,Gerencia
        João Silva,Maria Santos,TI
        Maria Santos,Pedro Costa,RH
        ```
        """)

        st.markdown("---")
        st.markdown("**💡 Dica:** O tamanho dos nós representa o número total de conexões de cada pessoa.")

    # Upload do arquivo
    uploaded_file = st.file_uploader(
        "📁 Faça upload do arquivo CSV",
        type=['csv'],
        help="Selecione um arquivo CSV com as colunas: Entrevistado, Alvo, Gerencia"
    )

    if uploaded_file is not None:
        try:
            # Ler o arquivo CSV
            df = pd.read_csv(uploaded_file)

            # Mostrar preview dos dados
            st.subheader("📊 Preview dos Dados")
            st.dataframe(df.head(10), use_container_width=True)

            # Mostrar estatísticas
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📝 Total de Registros", len(df))
            with col2:
                pessoas_unicas = len(set(df['Entrevistado'].dropna()) | set(df['Alvo'].dropna()))
                st.metric("👥 Pessoas Únicas", pessoas_unicas)
            with col3:
                st.metric("🏢 Gerências", df['Gerencia'].nunique())

            st.markdown("---")

            # Gerar gráfico
            if st.button("🚀 Gerar Gráfico de Rede", type="primary"):
                with st.spinner("⏳ Processando dados e criando o gráfico..."):
                    fig = criar_grafico_rede(df)

                    if fig is not None:
                        st.subheader("🕸️ Rede de Relacionamentos")
                        st.plotly_chart(fig, use_container_width=True)

                        # Informações adicionais
                        st.info("💡 **Como interpretar o gráfico:**\n"
                                "- Cada nó representa uma pessoa\n"
                                "- O tamanho do nó indica o número total de conexões\n"
                                "- As cores representam diferentes gerências\n"
                                "- Passe o mouse sobre os nós para ver detalhes")

        except Exception as e:
            st.error(f"❌ Erro ao ler o arquivo: {str(e)}")
            st.info("💡 Verifique se o arquivo está no formato correto e contém as colunas necessárias.")

    else:
        # Mostrar exemplo quando não há arquivo
        st.info("📁 Faça upload de um arquivo CSV para começar!")

        # Exemplo de dados
        st.subheader("📋 Exemplo de Estrutura de Dados")
        exemplo_df = pd.DataFrame({
            'Entrevistado': ['João Silva', 'Maria Santos', 'Pedro Costa', 'Ana Oliveira'],
            'Alvo': ['Maria Santos', 'Pedro Costa', 'Ana Oliveira', 'João Silva'],
            'Gerencia': ['TI', 'RH', 'Financeiro', 'Marketing']
        })
        st.dataframe(exemplo_df, use_container_width=True)


if __name__ == "__main__":
    main()