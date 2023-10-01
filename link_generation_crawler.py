from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json
from processor import *
import datetime as dt
from logger import log_to_db

def get_selectors(domain_subscription_id):
    with open("./link_generation.json", "r", encoding='utf-8') as f:
        domain_selectors = json.loads(f.read())
    return domain_selectors.get(str(domain_subscription_id))



def get_results(domain_subscription_id):
    subscription_selectors = get_selectors(domain_subscription_id)
    domains_subscription_id = subscription_selectors.get("domains_subscription_id")
    domain_name = subscription_selectors.get("name")

    urls_list = subscription_selectors.get("urls_list")
    is_active = subscription_selectors.get("is_active")
    wait_before_load = subscription_selectors.get("wait_before_load")
    scroll = subscription_selectors.get("scroll")
    base_url = subscription_selectors.get("base_url")
    type = subscription_selectors.get("type")
    run_js = subscription_selectors.get("run_js")
    for_loop = subscription_selectors.get("for_loop")
    selectors = subscription_selectors.get("selectors")
    selector_dict = []
    try:
        for domain_selectors in selectors:
            name = domain_selectors.get("name")
            price = domain_selectors.get("price")

            selector = domain_selectors.get("selector")
            attribute = domain_selectors.get("attribute")
            data_selector = {name: {

                "selector": selector,
                "attribute": attribute
            }
            }
            if price:
                for i in price:
                    name = i.get("name")

                    selector = i.get("selector")
                    attribute = i.get("attribute")

                    data_selector = {name: {

                            "selector": selector,
                            "attribute": attribute,
                        }
                        }
                    selector_dict.append(data_selector)

            selector_dict.append(data_selector)
    except Exception as e:
        log_to_db('ERROR', str(e))
    
    return domains_subscription_id, domain_name, urls_list, is_active, wait_before_load, scroll, base_url, type, run_js, for_loop, selector_dict



def open_browser(domain_id):
    domains_subscription_id, domain_name, urls_list, is_active, wait_before_load, scroll, base_url, type, run_js, for_loop, selector_dict = get_results(domain_id)
    if is_active:
        with sync_playwright() as playwright:
            chromium = playwright.firefox  # or "firefox" or "webkit".
            browser = chromium.launch(headless=False)
            context = browser.new_context(
                ignore_https_errors=True, user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36")
            page = context.new_page()
            page.set_default_navigation_timeout(1000000000)
            for url in urls_list:
                created_at = dt.datetime.now()
                log_to_db('INFO', f"Go to url: {url} as {created_at}")
                page.goto(url)
                page.wait_for_load_state()
                # bekletme koymak için
                #page.wait_for_timeout(5000000)
                if wait_before_load:
                    page.wait_for_timeout(wait_before_load)
                if run_js:
                    try:
                        page.evaluate(run_js)
                        page.wait_for_timeout(5000)
                    except Exception as e:
                        log_to_db('ERROR', str(e))
                page.wait_for_timeout(5000)
                page_content = page.content()
                soup = BeautifulSoup(page_content, 'html.parser')
                if type == "link_generation":
                    if scroll:
                        scroll_page(page)
                        
                    get_campaings_links(page, selector_dict, url, domain_id, base_url, for_loop, domain_name, run_js)

if __name__ == "__main__":
    domain_id_list = [1,2,3]
    created_at = dt.datetime.now()
    for domain_id in domain_id_list:
        print(f"Process Started with domain_id: {domain_id} as {created_at}")
        log_to_db('INFO', f"Process Started with domain_id: {domain_id} as {created_at}")
        open_browser(domain_id)