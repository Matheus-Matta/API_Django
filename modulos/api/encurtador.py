import requests
def encurtar_url_tinyurl(url):
                api_url = f"http://tinyurl.com/api-create.php?url={url}"
                response = requests.get(api_url)
                if response.status_code == 200:
                    return response.text  # URL encurtada
                else:
                    raise ValueError(f"Erro ao encurtar URL: {response.text}")
                    