import requests
from typing import Dict, Optional, Union

class DadJokeService:
    """
    A service layer for fetching dad jokes from an external API.
    
    Uses the icanhazdadjoke.com API to retrieve dad jokes.
    """
    
    BASE_URL = "https://icanhazdadjoke.com/"
    
    @classmethod
    def get_random_joke(cls) -> Dict[str, Union[str, int]]:
        """
        Fetch a random dad joke from the icanhazdadjoke.com API.
        
        Returns:
            Dict containing joke details:
            - 'id': Unique joke identifier
            - 'joke': The text of the dad joke
            - 'status': HTTP status code of the request
        
        Raises:
            requests.RequestException: If there's an error fetching the joke
        """
        headers = {
            "Accept": "application/json",
            "User-Agent": "Prometheus Swarm Dad Joke Service (github.com/your-repo)"
        }
        
        try:
            response = requests.get(cls.BASE_URL, headers=headers)
            response.raise_for_status()
            
            joke_data = response.json()
            return {
                "id": joke_data.get("id", ""),
                "joke": joke_data.get("joke", ""),
                "status": response.status_code
            }
        except requests.RequestException as e:
            return {
                "id": "",
                "joke": f"Error fetching joke: {str(e)}",
                "status": 500
            }
    
    @classmethod
    def get_joke_by_id(cls, joke_id: str) -> Dict[str, Union[str, int]]:
        """
        Fetch a specific dad joke by its ID.
        
        Args:
            joke_id (str): Unique identifier of the joke
        
        Returns:
            Dict containing joke details or error information
        """
        if not joke_id:
            return {
                "id": "",
                "joke": "Invalid joke ID provided",
                "status": 400
            }
        
        headers = {
            "Accept": "application/json",
            "User-Agent": "Prometheus Swarm Dad Joke Service (github.com/your-repo)"
        }
        
        try:
            response = requests.get(f"{cls.BASE_URL}j/{joke_id}", headers=headers)
            response.raise_for_status()
            
            joke_data = response.json()
            return {
                "id": joke_data.get("id", ""),
                "joke": joke_data.get("joke", ""),
                "status": response.status_code
            }
        except requests.RequestException as e:
            return {
                "id": joke_id,
                "joke": f"Error fetching joke: {str(e)}",
                "status": 500
            }