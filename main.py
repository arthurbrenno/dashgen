import pandas as pd
import json
import argparse
from bokeh.plotting import figure, output_file, save
from bokeh.models import (ColumnDataSource, CustomJS, Select, Slider,
                          TextInput, HoverTool)
from bokeh.layouts import column, row
from bokeh.embed import file_html
from bokeh.resources import CDN
from bokeh.models import Div

def ler_dados(caminho_arquivo):
    if caminho_arquivo.endswith('.csv'):
        dados = pd.read_csv(caminho_arquivo)
    elif caminho_arquivo.endswith('.json'):
        dados = pd.read_json(caminho_arquivo)
    else:
        raise ValueError("Formato de arquivo não suportado.")
    return dados

def criar_dashboard(dados, configuracoes, arquivo_saida):
    # Cria uma fonte de dados para o Bokeh
    source = ColumnDataSource(dados)
    ferramentas = configuracoes.get('ferramentas', 'pan,wheel_zoom,box_zoom,reset,save')
    titulo = configuracoes.get('titulo', 'Dashboard Interativo')
    x_axis_label = configuracoes.get('x_axis_label', '')
    y_axis_label = configuracoes.get('y_axis_label', '')
    tooltips = configuracoes.get('tooltips', [])

    # Cria a figura
    p = figure(title=titulo, tools=ferramentas, tooltips=tooltips)

    # Obtém o tipo de gráfico e parâmetros
    tipo_grafico = configuracoes.get('tipo_grafico', 'circle')
    parametros_grafico = configuracoes.get('parametros_grafico', {})
    x = parametros_grafico.get('x')
    y = parametros_grafico.get('y')

    # Plota o gráfico com base no tipo
    if tipo_grafico == 'circle':
        p.circle(x=x, y=y, source=source, **parametros_grafico.get('extras', {}))
    elif tipo_grafico == 'line':
        p.line(x=x, y=y, source=source, **parametros_grafico.get('extras', {}))
    elif tipo_grafico == 'bar':
        p.vbar(x=x, top=y, source=source, **parametros_grafico.get('extras', {}))
    else:
        raise ValueError("Tipo de gráfico não suportado.")

    p.xaxis.axis_label = x_axis_label
    p.yaxis.axis_label = y_axis_label

    # Lista para armazenar os widgets
    widgets = []

    # Adiciona filtros interativos
    filtros = configuracoes.get('filtros', [])
    for filtro in filtros:
        coluna = filtro['coluna']
        tipo = filtro['tipo']
        if tipo == 'select':
            opcoes = list(dados[coluna].unique())
            select = Select(title=filtro.get('titulo', coluna),
                            value=str(opcoes[0]),
                            options=[str(op) for op in opcoes])
            callback = CustomJS(args=dict(source=source, select=select, coluna=coluna), code="""
                const data = source.data;
                const valor = select.value;
                const original_data = source.data_original;
                const filtro_coluna = coluna;

                const new_data = {};
                for (let key in data) {
                    new_data[key] = [];
                }

                for (let i = 0; i < original_data[filtro_coluna].length; i++) {
                    if (original_data[filtro_coluna][i] == valor) {
                        for (let key in data) {
                            new_data[key].push(original_data[key][i]);
                        }
                    }
                }
                source.data = new_data;
                source.change.emit();
            """)
            select.js_on_change('value', callback)
            widgets.append(select)
        elif tipo == 'slider':
            minimo = filtro.get('minimo', dados[coluna].min())
            maximo = filtro.get('maximo', dados[coluna].max())
            passo = filtro.get('passo', (maximo - minimo) / 100)
            slider = Slider(start=minimo, end=maximo, value=maximo, step=passo, title=filtro.get('titulo', coluna))
            callback = CustomJS(args=dict(source=source, slider=slider, coluna=coluna), code="""
                const data = source.data;
                const threshold = slider.value;
                const original_data = source.data_original;
                const filtro_coluna = coluna;

                const new_data = {};
                for (let key in data) {
                    new_data[key] = [];
                }

                for (let i = 0; i < original_data[filtro_coluna].length; i++) {
                    if (original_data[filtro_coluna][i] <= threshold) {
                        for (let key in data) {
                            new_data[key].push(original_data[key][i]);
                        }
                    }
                }
                source.data = new_data;
                source.change.emit();
            """)
            slider.js_on_change('value', callback)
            widgets.append(slider)
        # Adicione outros tipos de filtros conforme necessário

    # Salva os dados originais para uso nos callbacks
    source.js_on_change('data', CustomJS(args=dict(source=source), code="""
        if (!('data_original' in source)) {
            source.data_original = Object.assign({}, source.data);
        }
    """))

    # Monta o layout
    layout = row(column(*widgets), p)

    # Gera o HTML completo
    html = file_html(layout, CDN, titulo)

    # Salva o arquivo HTML
    with open(arquivo_saida, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"Dashboard salvo em {arquivo_saida}")

def main():
    parser = argparse.ArgumentParser(description='Gerador de Dashboard Interativo')
    parser.add_argument('--dados', required=True, help='Caminho para o arquivo de dados')
    parser.add_argument('--config', required=True, help='Caminho para o arquivo de configuração')
    parser.add_argument('--saida', required=True, help='Caminho para o arquivo HTML de saída')
    args = parser.parse_args()

    # Ler os dados e as configurações
    dados = ler_dados(args.dados)
    with open(args.config, 'r', encoding='utf-8') as f:
        configuracoes = json.load(f)

    # Criar o dashboard interativo
    criar_dashboard(dados, configuracoes, args.saida)

if __name__ == "__main__":
    main()
