import streamlit as st
import pandas as pd
from datetime import datetime

# Initialize session state
if 'previous_calculations' not in st.session_state:
    st.session_state.previous_calculations = []

def validate_inputs(name, age, height, weight):
    """Validate user inputs and return error message if invalid."""
    if not name.strip():
        return "Please enter your name."
    if age < 1:
        return "Please enter a valid age."
    if height < 50:
        return "Please enter a valid height (minimum 50 cm)."
    if weight < 30:
        return "Please enter a valid weight (minimum 30 kg)."
    return None

def calculate_bmr_tdee(weight, height, age, gender, activity_level):
    """Calculate BMR and TDEE with error handling."""
    try:
        # BMR calculation using Mifflin-St Jeor Equation
        if gender == 'Male':
            bmr = 10 * weight + 6.25 * height - 5 * age + 5
        else:
            bmr = 10 * weight + 6.25 * height - 5 * age - 161
        
        # Activity level multipliers for TDEE
        activity_multipliers = {
            'Sedentary': 1.2,          # Little or no exercise
            'Lightly Active': 1.375,    # Light exercise 1-3 days/week
            'Moderately Active': 1.55,  # Moderate exercise 3-5 days/week
            'Very Active': 1.725,       # Heavy exercise 6-7 days/week
            'Extremely Active': 1.9     # Very heavy exercise, physical job
        }
        
        if activity_level not in activity_multipliers:
            raise ValueError(f"Invalid activity level: {activity_level}")
            
        tdee = bmr * activity_multipliers[activity_level]
        
        # Validate results
        if bmr <= 0 or tdee <= 0:
            raise ValueError("Invalid calculation result")
            
        return bmr, tdee
        
    except Exception as e:
        st.error(f"Error in calculations: {str(e)}")
        return None, None

def generate_plan(goals, tdee, weight):
    """Generate personalized diet and exercise plan."""
    try:
        if tdee is None:
            return 0, "Unable to generate diet plan.", "Unable to generate exercise plan."
        
        protein_needs = weight * 2.2  # Protein needs in grams (2.2g per kg)
        
        if goals == 'Weight Loss':
            calories = max(1200, tdee - 500)  # Minimum 1200 calories
            macros = {
                'protein': protein_needs,
                'carbs': (calories * 0.40) / 4,  # 40% carbs
                'fats': (calories * 0.25) / 9    # 25% fats
            }
            diet_plan = f"""
            Daily Targets:
            - Calories: {calories:.0f} kcal
            - Protein: {macros['protein']:.0f}g
            - Carbs: {macros['carbs']:.0f}g
            - Fats: {macros['fats']:.0f}g
            
            Focus on:
            - High protein foods (lean meat, fish, eggs)
            - Fiber-rich vegetables
            - Complex carbohydrates
            - Limited processed foods
            """
            exercise_plan = """
            Weekly Schedule:
            - 3-4 days of moderate-intensity cardio (30-45 minutes)
            - 2-3 days of strength training
            - Include rest days for recovery
            """
            
        elif goals == 'Muscle Gain':
            calories = tdee + 500
            macros = {
                'protein': protein_needs,
                'carbs': (calories * 0.50) / 4,  # 50% carbs
                'fats': (calories * 0.25) / 9    # 25% fats
            }
            diet_plan = f"""
            Daily Targets:
            - Calories: {calories:.0f} kcal
            - Protein: {macros['protein']:.0f}g
            - Carbs: {macros['carbs']:.0f}g
            - Fats: {macros['fats']:.0f}g
            
            Focus on:
            - High protein foods every 3-4 hours
            - Complex carbohydrates
            - Healthy fats
            - Pre and post-workout nutrition
            """
            exercise_plan = """
            Weekly Schedule:
            - 4-5 days of strength training
            - Focus on compound exercises
            - Progressive overload
            - 1-2 days of light cardio
            - Proper rest between sessions
            """
            
        elif goals == 'Maintenance':
            calories = tdee
            macros = {
                'protein': protein_needs,
                'carbs': (calories * 0.45) / 4,  # 45% carbs
                'fats': (calories * 0.30) / 9    # 30% fats
            }
            diet_plan = f"""
            Daily Targets:
            - Calories: {calories:.0f} kcal
            - Protein: {macros['protein']:.0f}g
            - Carbs: {macros['carbs']:.0f}g
            - Fats: {macros['fats']:.0f}g
            
            Focus on:
            - Balanced macro distribution
            - Whole, unprocessed foods
            - Regular meal timing
            - Adequate hydration
            """
            exercise_plan = """
            Weekly Schedule:
            - 3-4 days of strength training
            - 2-3 days of moderate cardio
            - Mix of activities for variety
            - Active recovery days
            """
            
        else:  # General Health
            calories = tdee
            diet_plan = """
            Focus on:
            - Balanced, nutrient-dense meals
            - Variety of fruits and vegetables
            - Whole grains and lean proteins
            - Mindful eating habits
            """
            exercise_plan = """
            Weekly Schedule:
            - Daily physical activity
            - Mix of cardio and strength training
            - Focus on enjoyable activities
            - Stay consistent with routine
            """
        
        return calories, diet_plan, exercise_plan
        
    except Exception as e:
        st.error(f"Error generating plan: {str(e)}")
        return tdee, "Error generating diet plan.", "Error generating exercise plan."

def create_download_data(user_data, calculations, plans):
    """Create formatted data for download."""
    return {
        'Personal Information': {
            'Name': user_data['name'],
            'Age': user_data['age'],
            'Gender': user_data['gender'],
            'Height (cm)': user_data['height'],
            'Weight (kg)': user_data['weight'],
            'Activity Level': user_data['activity_level'],
            'Goal': user_data['goals']
        },
        'Calculations': {
            'BMR': f"{calculations['bmr']:.2f} kcal/day",
            'TDEE': f"{calculations['tdee']:.2f} kcal/day",
            'Target Calories': f"{calculations['calories']:.2f} kcal/day"
        },
        'Plans': {
            'Diet Plan': plans['diet'],
            'Exercise Plan': plans['exercise']
        }
    }

def app():
    """Main Streamlit application."""
    st.set_page_config(page_title="Fitness Planner", layout="wide")
    
    st.title("🏋️‍♂️ Personalized Fitness Planner")
    
    # Create form for user inputs
    with st.form(key='profile_form'):
        col1, col2 = st.columns(2)
        
        with col1:
            st.header("📝 Personal Information")
            name = st.text_input("What's your name?", key="name")
            age = st.number_input("Age", min_value=1, max_value=120, value=25, step=1, key="age")
            gender = st.radio("Gender", options=['Male', 'Female'], key="gender")
            height = st.number_input("Height (in cm)", min_value=50.0, max_value=300.0, value=170.0, step=0.1, key="height")
            weight = st.number_input("Weight (in kg)", min_value=30.0, max_value=200.0, value=70.0, step=0.1, key="weight")
        
        with col2:
            st.header("🎯 Goals & Lifestyle")
            activity_level = st.selectbox(
                "How active are you?",
                ['Sedentary', 'Lightly Active', 'Moderately Active', 'Very Active', 'Extremely Active'],
                key="activity"
            )
            
            goals = st.selectbox(
                "What is your primary goal?",
                ['Weight Loss', 'Muscle Gain', 'Maintenance', 'General Health'],
                key="goals"
            )
            
            st.header("😴 Daily Routine")
            sleep_hours = st.slider("Hours of sleep per night", min_value=1, max_value=12, value=8, key="sleep")
            meals_per_day = st.slider("Meals per day", min_value=1, max_value=6, value=3, key="meals")

        submit_button = st.form_submit_button("Generate Plan")

    if submit_button:
        # Validate inputs
        error_message = validate_inputs(name, age, height, weight)
        if error_message:
            st.error(error_message)
            return

        # Calculate BMR and TDEE
        bmr, tdee = calculate_bmr_tdee(weight, height, age, gender, activity_level)
        
        if bmr is not None and tdee is not None:
            # Generate the personalized plan
            calories, diet_plan, exercise_plan = generate_plan(goals, tdee, weight)
            
            # Store calculation in session state
            calculation = {
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'name': name,
                'bmr': bmr,
                'tdee': tdee,
                'goal': goals,
                'calories': calories
            }
            st.session_state.previous_calculations.append(calculation)
            
            # Display Results
            st.header(f"👋 Hello, {name}!")
            
            # Create three columns for displaying results
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("BMR", f"{bmr:.0f} kcal/day")
            with col2:
                st.metric("TDEE", f"{tdee:.0f} kcal/day")
            with col3:
                st.metric("Target Calories", f"{calories:.0f} kcal/day")
            
            # Display detailed plans
            st.subheader("🍽️ Diet Plan")
            st.markdown(diet_plan)
            
            st.subheader("💪 Exercise Plan")
            st.markdown(exercise_plan)
            
            st.subheader("😴 Sleep & Meal Schedule")
            st.write(f"- Recommended sleep: {sleep_hours} hours per night")
            st.write(f"- Planned meals: {meals_per_day} per day")
            
            # Create download data
            plan_data = create_download_data(
                user_data={'name': name, 'age': age, 'gender': gender, 'height': height, 
                          'weight': weight, 'activity_level': activity_level, 'goals': goals},
                calculations={'bmr': bmr, 'tdee': tdee, 'calories': calories},
                plans={'diet': diet_plan, 'exercise': exercise_plan}
            )
            
            # Convert to DataFrame for download
            df = pd.DataFrame([plan_data])
            csv = df.to_csv(index=False).encode('utf-8')
            
            st.download_button(
                label="📥 Download Your Plan",
                data=csv,
                file_name=f"fitness_plan_{name}_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
            
            st.success("Plan generated successfully! Good luck on your fitness journey! 🌟")
            
            # Show previous calculations if any exist
            if len(st.session_state.previous_calculations) > 1:
                st.subheader("📊 Previous Calculations")
                prev_calc_df = pd.DataFrame(st.session_state.previous_calculations)
                st.dataframe(prev_calc_df)

if __name__ == "__main__":
    app()