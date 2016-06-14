import json
import requests
from pandas import DataFrame
from bs4 import BeautifulSoup

def scraper(data1,data2,indice,Sessao):

	url = "https://www3.bcb.gov.br/CALCIDADAO/publico/corrigirPorIndice.do?method=corrigirPorIndice"
	dados = {
		"aba":"1",
		"selIndice":indice,
		"dataInicial":data1,
		"dataFinal":data2,
		"valorCorrecao":"1"
	}
	cabecalho =  {
		'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Connection':'keep-alive',
        'Content-Length':'133',
        'Host':'www3.bcb.gov.br',
        'Origin':'https://www3.bcb.gov.br',
        'X-Requested-With':'XMLHttpRequest',
        'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36',
        'Content-Type':'application/x-www-form-urlencoded',
        'Referer':'https://www3.bcb.gov.br/CALCIDADAO/publico/exibirFormCorrecaoValores.do?method=exibirFormCorrecaoValores',
        'Accept-Encoding':'gzip, deflate, br',
        'Accept-Language':'en-US,en;q=0.8,pt;q=0.6,es;q=0.4,fr;q=0.2'
    }

	r = Sessao.post(url, data = dados, headers=cabecalho)
	fator = (float(r.text.split("Valor percentual")[1].split('class="fundoPadraoAClaro3 ">')[1].split(" %")[0].replace(",","."))/100)+1
	print(data1,data2,fator)
	return fator

def acha_intervalo(data1,data2,intervalo):
	data1 = [int(d) for d in data1.split("/")]
	data2 = [int(d) for d in data2.split("/")]
	datas = []
	if intervalo == "ano":
		dif = data2[1] - data1[1]
		for i in range(dif):
			data = str(data1[0]).zfill(2) + "/" + str(data1[1]+i+1)
			datas.append(data)
	elif intervalo == "mes":
		mes_atual = data1[0]
		ano_atual = data1[1]
		data_atual = int(str(data1[1])+str(data1[0]).zfill(2))
		data_final = int(str(data2[1])+str(data2[0]).zfill(2))
		while data_atual < data_final:
			if mes_atual < 12:
				mes_atual += 1
				data_atual += 1
			else:
				mes_atual = 1
				ano_atual += 1
				data_atual += 100
			data = str(mes_atual).zfill(2) + "/" + str(ano_atual)
			datas.append(data)

	return datas


def corrige(data1,data2,indice,intervalo):
	Sessao = requests.Session()
	url = "https://www3.bcb.gov.br/CALCIDADAO/publico/exibirFormCorrecaoValores.do?method=exibirFormCorrecaoValores"
	Sessao.get(url)
	datas = acha_intervalo(data1,data2,intervalo)
	dados = []

	for d in datas:
		dados.append(scraper(data1,d,indice,Sessao))

	dados = DataFrame(dados)
	dados.to_csv("correcao_indice.csv",index=None)


indices = {
	"igpm":"00189IGP-M",
	"igpdi":"00190IGP-DI",
	"incp":"00188INPC",
	"ipca":"00433IPC-A",
	"ipcae":"10764IPC-E",
	"ipcbrasil":"00191IPC-BRASIL",
	"ipcsp":"00193IPC-SP"
	}

intervalos = ["mes","ano"]

corrige("01/1995","01/1996",indices["ipca"],intervalos[0])
