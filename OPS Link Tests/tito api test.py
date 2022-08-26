import requests

tito_test = requests.get("https://api.tito.io/v3/hello", headers={"Authorization":"Token token=secret_2jyumm_qcZ23K_K3vzs5"}, verify=True)

tito_content = tito_test.content
print(tito_content)