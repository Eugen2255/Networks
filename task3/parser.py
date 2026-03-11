from playwright.sync_api import sync_playwright
import csv
import time

def parse(url="https://divoroom.store/catalog", headless=True):
    products = []
    
    with sync_playwright() as p:
        with p.chromium.launch(headless=headless) as browser:
            page = browser.new_page()
            
            page.goto(url, wait_until='networkidle', timeout=30000)
            
            page.wait_for_selector('.js-product.t-store__card', timeout=15000)
            time.sleep(0.5)
            
            # Нажимаем "загрузить ещё" пока не дойдём до конца
            while True:
                load_more_btn = page.locator('.js-store-load-more-btn-text').first
                
                if load_more_btn.count() > 0 and load_more_btn.is_visible():
                    load_more_btn.scroll_into_view_if_needed()
                    load_more_btn.click()
                    
                    try:
                        page.wait_for_load_state('networkidle', timeout=10000)
                    except:
                        pass
                    time.sleep(1)
                else:
                    break
            
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(1)
            
            cards = page.locator('.js-product.t-store__card').all()
            
            for _, card in enumerate(cards):
                try:
                    product = {}

                    product['product_id'] = card.get_attribute('data-product-uid')
                    
                    title_el = card.locator('.js-store-prod-name.t-store__card__title').first
                    product['title'] = title_el.text_content().strip()
                    
                    desc_el = card.locator('.js-store-prod-descr.t-store__card__descr').first
                    if desc_el.count() > 0:
                        desc = desc_el.text_content().strip()
                        product['description'] = desc 
                    
                    price_el = card.locator('.js-product-price.t-store__card__price-value').first
                    if price_el.count() > 0:
                        price_attr = price_el.get_attribute('data-product-price-def')
                        product['price'] = price_attr
                    
                    product_url = card.get_attribute('data-product-url')
                    if product_url:
                        product['url'] = product_url

                    product_img = card.get_attribute('data-product-img')
                    if product_img:
                        product['image'] = product_img.strip()

                    out_of_stock_btn = card.locator('text=Нет в наличии').first
                    product['in_stock'] = out_of_stock_btn.count() == 0
                    
                    products.append(product)
     
                except Exception as e:
                    print(f"Ошибка: {e}")
                    continue
    
    return products


if __name__ == "__main__":
    results = parse(headless=True)
    
    if results:
        with open('products.csv', 'w', encoding='utf-8-sig', newline='') as f:
            fieldnames = ['product_id', 'title', 'description', 'price', 'url', 'image', 'in_stock']
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(results)