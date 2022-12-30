import requests
from bs4 import BeautifulSoup


def get_latest_news() -> str:
    page = requests.get("https://www.canalmeio.com.br/ultima-edicao/")
    soup = BeautifulSoup(page.text)

    main_content = soup.findAll("section", {"class": "post_content clearfix"})
    if main_content:
        main_content = main_content[0]

        h1s = main_content.findAll("h1")
        h1s = h1s[0]

        ps = main_content.findAll("p")
        p_with_text = [x for x in ps if x.text]

        text_len = 0
        final_text = f"{h1s.text}. "
        for p in p_with_text:
            text_len = text_len + len(p.text)
            if text_len > 5000:
                break

            final_text = final_text + p.text + " "

    return final_text
