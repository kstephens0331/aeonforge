import os
from typing import Optional
from dotenv import load_dotenv

class APIKeyManager:
    """
    Manages API keys with human-in-the-loop approval system.
    Follows the Aeonforge rule: always ask before adding anything to .env
    """
    
    def __init__(self):
        load_dotenv()
        self._keys_cache = {}
    
    def get_api_key(self, service_name: str, key_name: str, description: str = "") -> Optional[str]:
        """
        Gets an API key for a service, asking the user if not found.
        
        Args:
            service_name: Name of the service (e.g., "Google Search", "Stripe")
            key_name: Environment variable name (e.g., "GOOGLE_API_KEY")
            description: Optional description of what the key is used for
            
        Returns:
            The API key if available, None if user declines
        """
        # First check if we already have it cached
        if key_name in self._keys_cache:
            return self._keys_cache[key_name]
            
        # Check environment variable
        api_key = os.getenv(key_name)
        if api_key:
            self._keys_cache[key_name] = api_key
            return api_key
        
        # Key not found - request from user
        return self._request_api_key_from_user(service_name, key_name, description)
    
    def _request_api_key_from_user(self, service_name: str, key_name: str, description: str) -> Optional[str]:
        """
        Requests an API key from the user with proper human-in-the-loop workflow.
        """
        print(f"\nAPI Key Required for {service_name}")
        print(f"=" * 40)
        print(f"Service: {service_name}")
        print(f"Environment Variable: {key_name}")
        
        if description:
            print(f"Purpose: {description}")
        
        print(f"\nTo use {service_name}, we need an API key.")
        print(f"Options:")
        print(f"1. Provide the API key now")
        print(f"2. Skip this operation")
        
        choice = input("\nEnter your choice (1/2): ").strip()
        
        if choice == "2":
            print(f"Skipping {service_name} operation.")
            return None
        elif choice == "1":
            api_key = input(f"\nEnter your {service_name} API key: ").strip()
            if not api_key:
                print("No API key provided. Skipping operation.")
                return None
            
            # Cache the key for this session
            self._keys_cache[key_name] = api_key
            
            # Ask if they want to save to .env
            print(f"\nSave to .env file for future use?")
            print(f"1. Yes, save to .env")
            print(f"2. No, just use for this session")
            
            save_choice = input("Enter your choice (1/2): ").strip()
            if save_choice == "1":
                self._offer_to_save_to_env(key_name, api_key)
            
            print(f"API key for {service_name} configured successfully!")
            return api_key
        else:
            print("Invalid choice. Skipping operation.")
            return None
    
    def _offer_to_save_to_env(self, key_name: str, api_key: str):
        """
        Offers to save the API key to .env file (following project rules).
        """
        print(f"\nSave to .env file")
        print(f"=" * 25)
        print(f"Would you like to save {key_name} to your .env file?")
        print(f"This will make it available for future sessions.")
        print(f"Warning: This will modify your .env file.")
        
        save_choice = input("Save to .env? (y/n): ").strip().lower()
        
        if save_choice == 'y':
            try:
                # Check if .env exists
                env_path = '.env'
                if os.path.exists(env_path):
                    # Read existing content
                    with open(env_path, 'r') as f:
                        content = f.read()
                    
                    # Check if key already exists
                    if f"{key_name}=" in content:
                        print(f"Warning: {key_name} already exists in .env file.")
                        overwrite = input("Overwrite existing value? (y/n): ").strip().lower()
                        if overwrite != 'y':
                            return
                        
                        # Replace existing key
                        lines = content.split('\n')
                        for i, line in enumerate(lines):
                            if line.startswith(f"{key_name}="):
                                lines[i] = f"{key_name}={api_key}"
                                break
                        content = '\n'.join(lines)
                    else:
                        # Append new key
                        content += f"\n{key_name}={api_key}"
                else:
                    # Create new .env file
                    content = f"{key_name}={api_key}"
                
                # Write to file
                with open(env_path, 'w') as f:
                    f.write(content)
                
                print(f"{key_name} saved to .env file successfully!")
                
            except Exception as e:
                print(f"Error saving to .env file: {e}")
        else:
            print(f"{key_name} will only be available for this session.")

# Global instance for easy access
api_key_manager = APIKeyManager()