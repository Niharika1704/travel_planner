import streamlit as st #web UI
from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI
from datetime import datetime,timedelta
import os

st.set_page_config(page_title="AI trip planner", page_icon="🤖",layout="wide")

st.session_state.setdefault("trip_plan", None)

def create_agent(api_key: str):
    os.environ["OPENAI_API_KEY"] = api_key

    city_expert = Agent(
        role="city expert",
        goal="Provide detailed information about the city, including attractions, local culture, and dining options.",
        backstory="You are a seasoned travel expert with deep knowledge of cities worldwide, their culture, hidden gems, and the best dining experiences.",
        verbose=True,
    )

    iterary_expert = Agent(
        role="itinerary expert",
        goal="Create a detailed day-by-day itinerary for the trip, including activities, dining, and transportation.",
        backstory="You are a travel agent with expertise in creating personalized travel itineraries based on user preferences and interests.",
        verbose=True,
    )

    return city_expert, iterary_expert 

def create_tasks(city_expert, iterary_expert, destination, start_date, end_date, interests):
    duration = (end_date - start_date).days + 1
    interests_str = ", ".join(interests)

    research_task = Task(
        description=f"""Research the destination {destination} and provide detailed information about attractions, local culture, and dining options based on the user's interests: {interests_str}.
        -top 5 must-see attractions
        -local culture highlights   
        -dining options that align with the user's interests
        """,
        agent=city_expert,
        expected_output="A comprehensive report on the destination, including a list of top attractions, cultural highlights, and dining options."
    )

    iterary_task = Task(
        description=f"""Create a detailed day-by-day itinerary for a {duration}-day trip to {destination} from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}, based on the user's interests: {interests_str}. Include activities, dining, and transportation details.""",
        agent=iterary_expert,
        expected_output="A detailed itinerary outlining daily activities, dining options, and transportation arrangements for the trip.",
        context=[research_task]
    )
    
    return [research_task, iterary_task]
def generate_trip_plan(api_key, destination, start_date, end_date, interests):
    city_expert, iterary_expert = create_agent(api_key)
    tasks = create_tasks(city_expert, iterary_expert, destination, start_date, end_date, interests)
    
    crew = Crew(agents=[city_expert, iterary_expert], tasks=tasks)
    crew.kickoff()
    
    trip_plan = {
        "destination": destination,
        "start_date": start_date,
        "end_date": end_date,
        "interests": interests,
         "itinerary": str(result)
    }
    
    return trip_plan

#sidebar 
with st.sidebar:
    st.header("confiuration")
    api_key = st.text_input("OpenAI API Key", type="password")
#main UI
st.title("AI Trip Planner")
st.markdown("Plan your next trip with the help of AI! Enter your destination, travel dates, and interests to get a personalized itinerary.")
col1,col2=st.columns(2)

with col1:
    st.subheader("Trip Details")
    origin= st.text_input("Origin",value= "New York")
    destination = st.text_input("Destination", value="Paris")
    start_date = st.date_input("Start Date", value=datetime.now().date() + timedelta(days=30))
    end_date = st.date_input("End Date", value=datetime.now().date() + timedelta(days=37))
    st.info(f"trip duration: {(end_date - start_date).days + 1} days")

with col2:
    st.subheader("preferences")
    interests=st.multiselect(
        "Select your interests",
        options=["Culture", "Food", "Nature", "History", "Art", "Adventure"],
        default=["Culture", "Food"]
    )
    budget= st.select_slider("Budget", options=["$", "$$", "$$$"], value="$$")
    travel_style= st.radio("Travel Style", options=["Relaxed", "Balanced", "Active"], index=1)

st.markdown("---")
_, col_btn, _ = st.columns([1, 2, 1])

with col_btn:
    if st.button("Generate Trip Plan"):
        if not api_key:
            st.error("Please enter your OpenAI API key in the sidebar.")
        elif not destination or not origin:
            st.error("Please enter both origin and destination.")
        elif not interests:
            st.error("Please select at least one interest .")
        elif start_date > end_date:
            st.error("End date must be after start date.")
        else:
            with st.status("Generating your trip plan...") as status:
                trip_plan = generate_trip_plan(api_key, destination, start_date, end_date, interests)
                st.session_state.trip_plan = trip_plan
                status.update(label="Trip plan generated successfully!", state="complete")
                st.success("Trip plan generated successfully!")

if st.session_state.trip_plan:
    duration=(end_date - start_date).days + 1
    st.success(f"Your {duration}-day trip to {destination} is ready!")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Destination", destination)
    col2.metric("route", f"{origin} → {destination}")
    col3.metric("budget", budget)
    col4.metric("travel style", travel_style)

    st.info(f"Interests: {', '.join(interests)}")
    st.markdown("your trip planner")
    st.markdown(st.session_state.trip_plan["itinerary"])

    col_d1, col_new, _=st.columns([1, 1, 2])
    col_d1.download_button(
        "download itenary",
        data=st.session_state.trip_plan["itinerary"],
        file_name=f"{destination}_trip_plan.txt",   
        mime="text/plain",
        use_container_width=True
    )

    if col_new.button("new plan", use_container_width=True):
        st.session_state.trip_plan = None
        st.rerun()
    
st.markdown("---")
st.markdown("Made with ❤️ by [Niharika Mirle](https://www.linkedin.com/in/niharika-mirle/)")
