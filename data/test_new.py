import requests

url = "https://www.topuniversities.com/rankings/endpoint?nid=4114613&page=1&items_per_page=150&tab=indicators&region=&countries=&cities=&search=&star=&sort_by=&order_by=&program_type=&scholarship=&fee=&english_score=&academic_score=&mix_student=&loggedincache=7047458-1778000320765&study_level=&subjects="

payload = {}
headers = {
  'Cookie': '__cf_bm=FcRDwBrxEb9sS9IljY1T9KnJDFryj2uM5NA3M7xAE5s-1778001219.8241532-1.0.1.1-hqar8XXZLRe7tWsGeKQN95_0g4weHnv_2CzfQ7KUY63G0guYV79.D3B1DXFh7AFeJmo5x9QL9vH6utiTEMQ47_5UNpvWKGdRDaALFnhSNq9YPFSA46nkh5B_kzRHyG9H; _cfuvid=0ppuSgiPnmObWNoKMxrxm6WPH0jVE.dNKHnm7xpv4xs-1778001219.8241532-1.0.1.1-x5_gNUQGynTs0.ngWcxqk8mMyoe.CpSzFK1x6aHYyQ8'
}

response = requests.request("GET", url, headers=headers, data=payload)

print(response.text)