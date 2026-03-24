import streamlit as st #web UI
from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI
from datetime import datetime,timedelta
import os

st.set_page_config(page_title="AI trip planner", page_icon="🤖",layout="wide")

st.session_state.setdefault("trip_plan", None)

def create_agent(api_key: str) -> Agent:
    llm = ChatOpenAI(model="gpt-4", api_key=api_key)

    city_expert = Agent(
        role="city expert",
        goal="Provide detailed information about the city, including attractions, local culture, and dining options.",
        verbose=True,
        llm=llm
    )
    
   
    iterary_expert = Agent(
        role="iterary expert",
        goal="Create a detailed day-by-day itinerary for the trip, including activities, dining, and transportation.",
        backstory="You are a travel agent with expertise in creating personalized travel itineraries based on user preferences and interests.",
        verbose=True,
        llm=llm
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
    crew.execute()
    
    trip_plan = {
        "destination": destination,
        "start_date": start_date,
        "end_date": end_date,
        "interests": interests,
        "itinerary": iterary_expert.output
    }
    
    return trip_plan

    
    
