import requests
def link_shortener(link):
    link_rep = link
    if "https://pastebin.com" in link:
        link_rep = "pob://pastebin/" + link[18:]
    url = "https://shorturl9.p.rapidapi.com/functions/api.php"

    payload = { "url": link_rep }
    headers = {
        "content-type": "application/x-www-form-urlencoded",
        "X-RapidAPI-Key": "0892048287msh96453ae8ed0f21fp11c894jsn438e9c6297a4",
        "X-RapidAPI-Host": "shorturl9.p.rapidapi.com"
    }
    response = requests.post(url, data=payload, headers=headers)
    data = response.json()
    if response.ok:
        if data.get("status") == "success":
            return data.get("url")
    return link