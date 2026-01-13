🏦 Painel Financeiro BC/SGS — Parte 1 do Desafio Técnico
1. Descrição do Projeto

Este projeto apresenta um painel financeiro dinâmico utilizando dados públicos do Banco Central do Brasil (SGS/BCData).
O objetivo é monitorar os principais indicadores econômicos — SELIC, USD/BRL e IPCA — com KPIs, insights automáticos e gráficos interativos.

O painel foi desenvolvido em Python com Streamlit e consome dados diretamente via API pública, garantindo atualização automática e reprodutibilidade.

2. Fonte de Dados

SELIC (Taxa de Juros) — Código 11
https://dadosabertos.bcb.gov.br/dataset/11-taxa-de-juros---selic

USD/BRL (Câmbio Livre - venda) — Código 1
https://dadosabertos.bcb.gov.br/dataset/1-taxa-de-cambio---livre---dolar-americano-venda---diario

IPCA (Variação Mensal %) — Código 433
https://www3.bcb.gov.br/sgspub/consultarvalores/consultarValoresSeries.do?method=consultarSeries&series=433

Formato de dados: JSON (via API).

3. Janela Temporal

O painel permite selecionar períodos de 12, 24 ou 36 meses.

Todos os KPIs, insights e gráficos se ajustam dinamicamente ao período selecionado.

4. KPIs Calculados
Indicador	Valor Atual	Descrição
SELIC	Último valor disponível	Variação em 30 dias
USD/BRL	Último valor disponível	Retorno % em 7 dias e 30 dias
Volatilidade USD/BRL 30d	Desvio padrão anualizado dos retornos diários	Mede a volatilidade recente
IPCA Acumulado 12m	Acumulado dos últimos 12 meses	Comparado à meta de inflação (3,5%)
5. Insights Automáticos

O painel gera insights dinâmicos baseados nos dados atuais:

SELIC Tendência — Indica se houve alta significativa nos últimos 30 dias.

USD/BRL Força Relativa — Compara o valor atual do USD com a média móvel de 30 dias.

IPCA x Meta — Indica se o acumulado dos últimos 12 meses está acima ou dentro da meta de inflação (3,5%).

Estes insights mudam automaticamente conforme o período selecionado e os dados mais recentes.

6. Visualizações

Gráficos interativos por Plotly:

Evolução da SELIC

Evolução do USD/BRL com média móvel de 30 dias

Evolução mensal do IPCA

Hierarquia clara:

KPIs no topo para leitura executiva rápida

Insights destacados para decisões estratégicas

Gráficos detalhando evolução e tendências

7. Como Executar

Instale as dependências:

pip install streamlit pandas numpy requests plotly


Execute o dashboard:

streamlit run dashboard_bc.py


Selecione o período de análise no menu suspenso e explore KPIs, insights e gráficos.

8. Premissas de Cálculo

SELIC variação 30 dias: (valor atual / valor 30 dias atrás - 1) * 100

USD/BRL retorno 7/30 dias: (valor atual / valor N dias atrás - 1) * 100

Volatilidade USD/BRL 30 dias: desvio padrão anualizado dos retornos diários dos últimos 30 dias

IPCA acumulado 12 meses: prod(1 + ipca_mensal/100) - 1

9. Estrutura de Pastas
desafio/
│
├─ script/
│   └─ dashboard_bc.py        # Código do dashboard
│
├─ dados/                     # CSVs salvos (opcional)
│   ├─ selic.csv
│   ├─ usd.csv
│   └─ ipca.csv
│
└─ README.md                  # Este arquivo