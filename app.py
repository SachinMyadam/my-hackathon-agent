import streamlit as st
import google.generativeai as genai

# --- CONFIGURATION ---
st.set_page_config(page_title="Grocery Helper", page_icon="🛒")

# --- UI & SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3724/3724720.png")
    st.title("🛒 AI Grocery Helper")
    st.markdown("""
    Welcome! I'm your smart grocery assistant.
    - Keep track of your grocery list.
    - Suggest recipes based on items you have.
    - Organize your list by supermarket aisle.
    - Plan your meals for the week!
    """)
    st.divider()

    if st.button("Plan My Meals for the Week"):
        st.session_state.messages.append({"role": "user", "content": "Please act as a meal planner and create a simple 7-day dinner plan. After you provide the plan, generate a complete grocery list for it."})
        st.rerun()

    if st.button("Estimate Total Price"):
        st.session_state.messages.append({"role": "user", "content": "Based on my list, what is the estimated total price?"})
        st.rerun()

    if st.button("Clear Conversation"):
        st.session_state.messages = []
        st.session_state.grocery_list = "Your grocery list is currently empty."
        st.rerun()

    st.divider()

    st.header("My Grocery List")
    if "grocery_list" not in st.session_state:
        st.session_state.grocery_list = "Your grocery list is currently empty."

    if st.button("Update List Display"):
        summary_prompt = "Based on our entire conversation, please give me just the final, clean, and complete grocery list as a simple bulleted list. Do not add any other text, just the list."
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(str(st.session_state.messages) + "\n\n" + summary_prompt)
        st.session_state.grocery_list = response.text

    st.markdown(st.session_state.grocery_list)

# --- MAIN APP TITLE ---
st.title("🤖 My Gemini Chatbot")

# --- AI & MODEL SETUP ---
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception:
    st.error("ERROR: Could not configure Google AI. Please check your API key.")
    st.stop()

# --- CHAT LOGIC ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if user_prompt := st.chat_input("What do you need?"):
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                persona = """
                You are an AI Grocery List assistant. Your job is to help the user manage their shopping list.
                - When the user adds items, confirm what you've added.
                - The user's list is the conversation history. When they ask "what's on my list?", review the chat history to tell them.
                - If the user asks you to organize the list, group items by common supermarket categories (e.g., Produce, Dairy, Bakery, Meat, Canned Goods).
                - If the user asks for a recipe, provide a simple one based on the ingredients they mention.
                - If the user asks for a price estimate, provide a rough guess for the total cost of the items on the list.
                - If the user asks you to be a meal planner, create a 7-day dinner plan and then provide a full grocery list for all the ingredients needed for that plan.
                - Keep your responses friendly and clear.
                """
                
                full_conversation = st.session_state.messages
                model_prompt = persona + "\n\nHere is the conversation so far:\n" + str(full_conversation)
                
                response = model.generate_content(model_prompt)
                assistant_response = response.text
                st.markdown(assistant_response)
                st.session_state.messages.append({"role": "assistant", "content": assistant_response})

            except Exception as e:
                st.error(f"An error occurred: {e}")