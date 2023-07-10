import time
import pandas as pd
import nltk
import warnings
import requests
import io
import os
from unidecode import unidecode


warnings.filterwarnings("ignore", message="DataFrame is highly fragmented.")
warnings.simplefilter(action='ignore', category=UserWarning)


 

# Função busca por nomes com distancia nltk de 1 ou 2. Essa biblioteca basicamente gera a distância
# entre duas strings, ou seja, quantas vezes devo modificar a string1 para chegar até a string2
# os valores 1 e 2 foram testados empiricamente e geraram resultados satisfatórios. Ele está pegando
# erros de digitação como: usuário escreve luiz e depois lluiz, amanda colocou ammanda, etc.
def remove_duplicado(lista3):
    lista_corretos = []
    lista_duplicados = []
    for i in range(len(lista3)):
        duplicado = False
        for j in range(i+1, len(lista3)):
            if i!=j and (nltk.edit_distance(lista3[i],lista3[j]) == 1 or
                nltk.edit_distance(lista3[i],lista3[j]) == 2):
                lista_corretos.append(lista3[j])
                lista_duplicados.append(lista3[i])
    return lista_corretos, lista_duplicados
ano = 2023



username =  os.environ['username']
password =  os.environ['password']



 

# Utiliza API do jira para gerar relatório de chamados
# Nessa etapa, ocultei o URL que utilizei. Para encontrá-lo, basta utilizar a biblioteca "jira" do python, realizando as Jqueries necessárias para gerar um arquivo .csv
url = os.environ['URL']

headers = {'Accept': 'text/csv'}
response = requests.get(url, headers=headers, auth=(username, password))



 

# Checar se a resposta foi bem-sucedida (status code 200), cria um dataset com resposta obtida e
# printa quantidade de chamados que foram obtidos via API. Tenho uma preocupação de que haja algum limite
# dessa API para + de 1000 registros
if response.status_code == 200:
    data = response.text
    df = pd.read_csv(io.StringIO(data), delimiter=';', parse_dates=['Created'], dayfirst=True)
    print(f'\nNúmero de chamados encontrados: {df.shape[0]}')
else:
    print('Falha na requisição da API do JIRA, código de resposta:', response.status_code)



# Tratativa da variável nomes: retiradas as aspas, em casos de mais de um participante, separei isso
# em uma lista e depois explodi ela, gerando novas linhas para cada participante (mantendo restante das
# colunas)
df.rename(columns={'Custom field (Participantes)': 'Participantes'}, inplace=True)
df['Participantes'] = df['Participantes'].str.lower()
df = df[df['Created'].dt.year == int(ano)]

# Os dados recebidos são, por padrão, criados com aspas e cada nome é separado por ;
# ex: "fulano.silva;beltrano.nunes;ciclano;borges"
df['Participantes'] = df['Participantes'].map(str).str.replace('"','').str.split(';')
df['Participantes'] = df['Participantes'].apply(lambda x: [p.strip() for p in x if p.strip()])
df = df.dropna(subset=['Participantes'])
df = df.explode('Participantes')
df['Participantes'] = df['Participantes'].astype(str)

# Alguns testes são realizados e, por padrão, vêm com participante 'teste'
df = df[~df['Participantes'].str.contains('teste')]

# unidecode foi utilizado para transformar ç em c e  remover acentos, o que 
# se tornou necessário por não haver um padrão nos nomes registrados
df['Participantes'] = df['Participantes'].apply(unidecode)
df = df.reset_index(drop=True)
 

# Exclui nomes incorretos, gerados pela função remove_duplicado e cria um dataframe contendo
# itens que foram considerados idênticos. Esse dataframe é exportado para o excel futuramente para
# conferência se o algoritmo está satisfatório
nomes_corretos_comparação, nomes_incorretos = remove_duplicado(df['Participantes'].unique())
df = df[~df['Participantes'].isin(nomes_incorretos)]
df = df[df['Participantes'] != 'nan']
valores_excluidos = {'Nome excluído': nomes_incorretos, 'Nome mantido': nomes_corretos_comparação}
valores_excluidos = pd.DataFrame(valores_excluidos)


# Gera um relatório com quantos colaboradores registraram em cada mês
primeiros_chamados = df.sort_values('Created').groupby('Participantes', as_index=False).first()
primeiros_chamados['Mes'] = primeiros_chamados['Created'].dt.month
quantitativo_meta = primeiros_chamados.groupby('Mes')['Participantes'].count()
meses = [i for i in range(1,13)]
idx = pd.Index(meses, name='Mes')
quantitativo_meta = quantitativo_meta.reindex(idx, fill_value=0)
quantitativo_meta = pd.DataFrame(quantitativo_meta, columns=['Participantes'])
quantitativo_meta['Participantes (%)'] = (quantitativo_meta['Participantes'] * (100 / 477)).round(2).map('{:.2f}%'.format)

 

# Gera um relatório com a lista dos registros para servir de conferência do quantitativo acima
relatorio_mes = primeiros_chamados.loc[:,['Issue key','Created','Mes','Participantes','Issue Type']].sort_values(['Mes','Created'])
relatorio_mes = relatorio_mes.reset_index()
relatorio_mes = relatorio_mes.drop(['index'], axis=1)
relatorio_mes.rename(columns={'Issue key': 'Chamado','Created': 'Data e Hora do Chamado','Issue Type': 'Tipo'}, inplace = True)


 

# Cria a pasta Meta_Gerada_Programa para salvar todos os arquivos nela
folder_path = "Meta_Gerada_Programa"
if not os.path.exists(folder_path):
    os.makedirs(folder_path)


# Salva todos os dataframes relevantes necessários num arquivo chamado
# Relatório meta de aderência-[Data de hoje].xlsx
dia_hoje = time.strftime("%d-%m-%Y")
nome_arquivo = f"Relatorio meta de aderência-{dia_hoje}.xlsx"
file_path = os.path.join(folder_path, nome_arquivo)
writer = pd.ExcelWriter(file_path, engine='xlsxwriter')
quantitativo_meta.to_excel(writer, sheet_name='Quantitativo mensal')
relatorio_mes.to_excel(writer, sheet_name='Relatório')
valores_excluidos.to_excel(writer, sheet_name='Nomes duplicados')
writer.close()
 

print(f'Arquivo salvo com sucesso!\n')
print(f'Nome do arquivo: {file_path}\n')
input('Digite enter para fechar...')