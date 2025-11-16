import requests
from bs4 import BeautifulSoup
import time

class SteamSearcher:
    def __init__(self):
        self.base_url = "https://store.steampowered.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
    def search_games_with_discount(self, min_discount=0, search_term="", max_results=25):
        """Search for games with discounts on Steam"""
        results = []
        
        try:
            # Use Steam's search API
            params = {
                'term': search_term,
                'category1': 998,  # Games
                'specials': 1,  # Only specials/deals
            }
            
            url = f"{self.base_url}/search/"
            response = requests.get(url, params=params, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find all game entries
                game_items = soup.find_all('a', class_='search_result_row')
                
                for item in game_items[:max_results]:
                    try:
                        # Extract game information
                        title_elem = item.find('span', class_='title')
                        title = title_elem.text.strip() if title_elem else "Unknown"
                        
                        # Get discount percentage
                        discount_elem = item.find('div', class_='discount_pct')
                        if discount_elem:
                            discount_text = discount_elem.text.strip().replace('-', '').replace('%', '')
                            discount = int(discount_text) if discount_text else 0
                        else:
                            discount = 0
                        
                        # Skip if below minimum discount
                        if discount < min_discount:
                            continue
                        
                        # Get prices
                        price_elem = item.find('div', class_='discount_final_price')
                        final_price = price_elem.text.strip() if price_elem else "N/A"
                        
                        original_price_elem = item.find('div', class_='discount_original_price')
                        original_price = original_price_elem.text.strip() if original_price_elem else final_price
                        
                        # Get app ID and URL
                        steam_link = item.get('href', '')
                        
                        results.append({
                            'title': title,
                            'discount': discount,
                            'original_price': original_price,
                            'final_price': final_price,
                            'url': steam_link
                        })
                        
                    except Exception as e:
                        print(f"Error parsing game entry: {e}")
                        continue
                        
        except Exception as e:
            print(f"Error searching Steam: {e}")
            raise Exception(f"Failed to search Steam: {str(e)}")
        
        return results
    
    def get_featured_deals(self, min_discount=0):
        """Get featured deals from Steam"""
        return self.search_games_with_discount(min_discount=min_discount, search_term="", max_results=50)
