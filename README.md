# 🌍 Mapa Global de Notícias sobre COVID-19

Este projeto gera um **mapa interativo em HTML** com base em notícias recentes do Google News sobre a pandemia de **COVID-19**, organizadas por países e regiões do mundo.  
Cada execução do script coleta notícias em tempo real (últimos _N_ dias) e atualiza automaticamente o mapa com **pontos clicáveis** que mostram título, data e link da notícia.

---

## ⚙️ Como funciona

1. O script consulta o **Google News (RSS)** para cada país/região configurado em `TARGETS`.  
2. Faz o download das notícias usando `requests` + `feedparser`, com **timeout, retries e User-Agent** para evitar bloqueios.  
3. Filtra as notícias pela janela definida em `DAYS_BACK` (padrão: 15 dias).  
4. Limita o número de notícias por região (`MAX_PER_AREA`) para não sobrecarregar o mapa.  
5. Gera o arquivo `mapa_covid_noticias_global.html`, que pode ser aberto em qualquer navegador.  

---

## 🚀 Instalação

Clone este repositório ou copie o script `mapa_covid_noticias_global.py` para a sua máquina.

Instale as dependências:

```bash
pip install folium feedparser python-dateutil requests
```

---

## ▶️ Uso

Execute o script:

```bash
python mapa_covid_noticias_global.py
```

Será gerado o arquivo:

```
mapa_covid_noticias_global.html
```

Abra-o no navegador e explore os pontos no mapa.  
Cada ponto mostra:
- Nome do país/região
- Título da notícia
- Data de publicação
- Link direto para a matéria

---

## 🌐 Países/Regiões monitorados

Atualmente estão configurados:

- **América do Sul**: Brasil, Argentina, Chile, Colômbia, Peru  
- **América do Norte**: EUA, Canadá, México  
- **Europa**: Reino Unido, França, Alemanha, Espanha, Itália, Portugal  
- **África**: África do Sul, Nigéria, Egito  
- **Ásia**: Índia, China, Japão, Coreia do Sul  
- **Oriente Médio**: Israel, Arábia Saudita, Emirados Árabes Unidos  
- **Oceania**: Austrália, Nova Zelândia  
- **Local extra**: Manaus (AM)

👉 Para adicionar ou remover regiões, basta editar o dicionário `TARGETS` no código.

---

## 🔄 Atualização dos dados

- O mapa é **atualizado sempre que o script é executado**.  
- Para “quase tempo real”, é possível agendar a execução:
  - **Windows**: Agendador de Tarefas (Task Scheduler)  
  - **Linux/Mac**: `cron`  

Exemplo (Linux, atualização diária às 9h):
```cron
0 9 * * * /usr/bin/python3 /caminho/mapa_covid_noticias_global.py
```

---

## 🛠️ Configurações importantes

- `DAYS_BACK`: janela de tempo (padrão: 15 dias).  
- `MAX_PER_AREA`: máximo de notícias por país/região (padrão: 12).  
- `USE_CLUSTER`: se `True`, agrupa pontos próximos em clusters.  

---

## 📂 Estrutura do projeto

```
.
├── mapa_covid_noticias_global.py   # Script principal
├── README.md                       # Documentação
└── mapa_covid_noticias_global.html # Saída (gerado a cada execução)
```

---

## 📌 Exemplo de uso

1. Execute o script.  
2. Abra o arquivo gerado no navegador.  
3. Clique nos marcadores vermelhos para ver os títulos e links das notícias.  

---

## ⚠️ Observações

- O Google News RSS pode variar conforme país/idioma. Se alguma região não gerar notícias, ajuste os parâmetros `hl`, `gl` e `ceid` no dicionário `TARGETS`.  
- Requer **conexão com a internet**.  
- Caso queira monitorar **outros temas** (ex.: “gripe aviária”, “dengue”), basta trocar as consultas (`q`) em `TARGETS`.

---

🔍 Projeto feito para investigação e monitoramento de surtos de **COVID-19 no noticiário global**.  
