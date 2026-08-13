# Ngpt_chat.py - Complete Standalone Chat Application
# Your friends just double-click and use their own API key!

import sys
import os
import json
import time
import base64
from datetime import datetime
from openai import OpenAI

# Configuration file name
CONFIG_FILE = "Ngpt_config.json"

def clear_screen():
    """Clear terminal screen for cleaner UI"""
    os.system('cls' if os.name == 'nt' else 'clear')

def load_config():
    """Load saved API key if it exists"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                encoded_key = config.get('api_key_encoded', '')
                if encoded_key:
                    # Decode the key
                    decoded_key = base64.b64decode(encoded_key.encode()).decode()
                    return decoded_key
        except:
            return ''
    return ''

def save_config(api_key):
    """Save API key securely (obfuscated)"""
    try:
        # Simple obfuscation to hide plain text
        encoded_key = base64.b64encode(api_key.encode()).decode()
        
        config = {
            'api_key_encoded': encoded_key,
            'saved_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        return True
    except:
        return False

def delete_config():
    """Delete saved configuration"""
    if os.path.exists(CONFIG_FILE):
        os.remove(CONFIG_FILE)
        return True
    return False

def test_api_key(api_key):
    """Test if API key is valid and working"""
    try:
        test_client = OpenAI(
            api_key=api_key,
            base_url='https://api.gapgpt.app/v1',
            timeout=10
        )
        
        # Make a minimal test request
        response = test_client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": "OK"}],
            max_tokens=2,
            temperature=0
        )
        return True, "API key is valid!"
    except Exception as e:
        error_msg = str(e)
        if "invalid" in error_msg.lower() or "authentication" in error_msg.lower():
            return False, "Invalid API key. Please check and try again."
        elif "rate" in error_msg.lower():
            return False, "Rate limit exceeded. Please try again later."
        else:
            return False, f"Connection error: {error_msg[:100]}"

def get_api_key():
    """Get API key from user (first time or if saved key is invalid)"""
    clear_screen()
    
    print("="*70)
    print("                      NGPT CHAT ASSISTANT  ")
    print("="*70)
    print("\n📌 FIRST TIME SETUP")
    print("-"*70)
    print("\nTo use this application, you need an OpenAI API key.")
    print("\n📍 How to get your API key:")
    print("   1. Go to: https://gapgpt.app/")
    print("   2. Sign up or log in to your gapgpt account")
    print("   3. go to api keys section")
    print("   4. Click 'Create new secret key'")
    print("   5. Copy the key (starts with 'sk-')")
    print("\n💰 Pricing:")
    print("   - New accounts get $0.50 free credit")
    print("   - GPT-4o costs ~$0.0025 per message")
    print("   - 200 messages ≈ $0.50")
    print("\n🔒 Privacy:")
    print("   ✓ Your API key is stored ONLY on YOUR computer")
    print("   ✓ The app creator CANNOT see your key")
    print("   ✓ You can delete the config file anytime")
    print("-"*70)
    
    while True:
        print("\n please Enter your OpenAI API Key: ", end="")
        api_key = input().strip()
        
        if not api_key:
            print("\n❌ API key cannot be empty! Please try again.")
            continue
        
        if not api_key.startswith('sk-'):
            print("\n  Warning: API keys usually start with 'sk-'")
            confirm = input("Continue anyway? (yes/no): ").lower()
            if confirm != 'yes':
                continue
        
        print("\n🔍 Testing your API key...")
        time.sleep(1)
        
        is_valid, message = test_api_key(api_key)
        
        if is_valid:
            print("\n✅ " + message)
            save_choice = input("\n💾 Save this API key for future use? (yes/no): ").lower()
            if save_choice == 'yes':
                save_config(api_key)
                print("✅ API key saved securely on your computer!")
            else:
                print("⚠️  You'll need to enter the key again next time.")
            
            print("\n✅ Setup complete! Starting chat...")
            time.sleep(2)
            return api_key
        else:
            print(f"\n❌ {message}")
            retry = input("\n🔄 Try again? (yes/no): ").lower()
            if retry != 'yes':
                print("\n👋 Goodbye!")
                sys.exit(0)

def save_conversation(messages):
    """Save chat history to a text file"""
    try:
        filename = f"chat_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("="*60 + "\n")
            f.write(f"NGPT CHAT LOG - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*60 + "\n\n")
            
            for msg in messages:
                f.write(f"{msg['role']}: {msg['content']}\n")
                f.write("-"*40 + "\n\n")
        
        return filename
    except Exception as e:
        return None

def show_help():
    """Display help menu"""
    print("\n" + "="*60)
    print("📖 COMMAND LIST")
    print("="*60)
    print("/exit or /quit - Exit the application")
    print("/clear - Clear the screen")
    print("/save - Save current conversation to file")
    print("/newkey - Change your API key")
    print("/help - Show this help menu")
    print("/stats - Show conversation statistics")
    print("="*60)

def main():
    """Main chat application"""
    clear_screen()
    
    # Try to load saved API key
    saved_key = load_config()
    
    if saved_key:
        # Test if saved key still works
        print("🔍 Checking saved API key...")
        is_valid, message = test_api_key(saved_key)
        
        if is_valid:
            print("✅ " + message)
            api_key = saved_key
            time.sleep(1)
        else:
            print(f"⚠️  Saved key issue: {message}")
            print("🔄 Please enter a new API key...")
            time.sleep(2)
            api_key = get_api_key()
    else:
        # No saved key, ask for one
        api_key = get_api_key()
    
    # Initialize OpenAI client with user's key
    client = OpenAI(
        api_key=api_key,
        base_url='https://api.gapgpt.app/v1'
    )
    
    clear_screen()
    
    # Welcome screen
    print("="*70)
    print("                      NGPT CHAT ASSISTANT  ")
    print("="*70)
    print(f"\n✅ Connected successfully!")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n💡 TIPS:")
    print("   • Type /help to see all commands")
    print("   • Type /newkey to change your API key")
    print("   • Type /save to save conversation")
    print("   • Type /exit to quit")
    print("-"*70)
    
    conversation_history = []
    total_messages = 0
    total_tokens = 0
    
    while True:
        try:
            # Get user input
            user_input = input("\n👤 You: ").strip()
            
            # Handle commands
            if user_input.lower() in ['/exit', '/quit', 'exit', 'quit']:
                print("\n👋 Goodbye! Thanks for chatting!")
                if conversation_history:
                    filename = save_conversation(conversation_history)
                    if filename:
                        print(f"💾 Conversation saved to: {filename}")
                print(f"\n📊 Session Statistics:")
                print(f"   • Messages exchanged: {total_messages}")
                print(f"   • Total tokens used: {total_tokens}")
                print(f"   • Estimated cost: ${total_tokens * 0.0000025:.4f}")
                time.sleep(2)
                break
                
            elif user_input.lower() in ['/clear', 'clear']:
                clear_screen()
                print("="*70)
                print("                      NGPT CHAT ASSISTANT  ")
                print("="*70)
                print("\n✨ Screen cleared!")
                print("-"*70)
                continue
                
            elif user_input.lower() in ['/save', 'save']:
                if conversation_history:
                    filename = save_conversation(conversation_history)
                    if filename:
                        print(f"✅ Conversation saved to: {filename}")
                    else:
                        print("❌ Failed to save conversation")
                else:
                    print("📝 No messages to save yet!")
                continue
                
            elif user_input.lower() in ['/newkey', 'newkey']:
                print("\n🔄 Changing API key...")
                delete_config()
                api_key = get_api_key()
                client = OpenAI(
                    api_key=api_key,
                    base_url='https://api.gapgpt.app/v1'
                )
                print("✅ API key changed successfully!")
                continue
                
            elif user_input.lower() in ['/help', 'help', '/?']:
                show_help()
                continue
                
            elif user_input.lower() in ['/stats', 'stats']:
                print("\n📊 CONVERSATION STATISTICS")
                print("="*40)
                print(f"Messages in this session: {total_messages}")
                print(f"Total tokens used: {total_tokens}")
                print(f"Estimated cost: ${total_tokens * 0.0000025:.4f}")
                print(f"Conversation turns: {len(conversation_history)//2}")
                print("="*40)
                continue
                
            elif not user_input:
                print("⚠️  Please enter a message or command!")
                continue
            
            # Send to API
            print("  AI: ", end="", flush=True)
            
            try:
                start_time = time.time()
                
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": user_input}],
                    temperature=0.7,
                    max_tokens=1000
                )
                
                end_time = time.time()
                answer = response.choices[0].message.content
                
                # Display answer
                print(answer)
                
                # Get token usage
                tokens_used = response.usage.total_tokens if hasattr(response, 'usage') else 0
                response_time = end_time - start_time
                
                # Show metadata
                print(f"\n   {response_time:.1f}s | 📊 {tokens_used} tokens | 💰 ~${tokens_used * 0.0000025:.4f}")
                
                # Save to history
                conversation_history.append({"role": "You", "content": user_input})
                conversation_history.append({"role": "AI", "content": answer})
                total_messages += 2
                total_tokens += tokens_used
                
            except Exception as e:
                error_msg = str(e)
                print(f"\n❌ Error: {error_msg}")
                
                if "authentication" in error_msg.lower() or "api key" in error_msg.lower():
                    print("\n🔑 Your API key appears to be invalid or expired.")
                    print("💡 Type '/newkey' to enter a new API key")
                elif "rate" in error_msg.lower():
                    print("\n⏰ Rate limit exceeded. Please wait a moment and try again.")
                elif "timeout" in error_msg.lower():
                    print("\n🌐 Connection timeout. Please check your internet connection.")
                else:
                    print("\n💡 Check your internet connection and try again.")
                
                continue
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye! Thanks for chatting!")
            if conversation_history:
                filename = save_conversation(conversation_history)
                if filename:
                    print(f"💾 Conversation saved to: {filename}")
            break
        except Exception as e:
            print(f"\n❌ Unexpected error: {str(e)}")
            print("💡 Please restart the application if issues persist.")

if __name__ == "__main__":
    main()
            