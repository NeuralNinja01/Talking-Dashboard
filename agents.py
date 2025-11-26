import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from groq import Groq
import json
import io

# --- Base Client ---
class GroqClient:
    def __init__(self, api_key):
        self.client = Groq(api_key=api_key)
        self.model = "moonshotai/kimi-k2-instruct-0905"

    def get_completion(self, prompt, system_message="You are a helpful assistant."):
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt},
                ],
                model=self.model,
                temperature=0.1, # Low temperature for deterministic code generation
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            return f"Error: {e}"

# --- Agent 1: The Data Janitor ---
class DataJanitor:
    def __init__(self):
        pass

    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Autonomously cleans the data:
        1. Fills missing values (numeric with mean, categorical with mode).
        2. Drops duplicates.
        3. Converts object columns to datetime if they look like dates.
        """
        df_clean = df.copy()

        # Drop duplicates
        df_clean = df_clean.drop_duplicates()

        # Handle missing values
        for col in df_clean.columns:
            if df_clean[col].dtype == 'object':
                # Try to convert to datetime
                try:
                    df_clean[col] = pd.to_datetime(df_clean[col])
                except (ValueError, TypeError):
                    # If not datetime, fill NA with mode
                    if df_clean[col].isnull().any():
                        mode_val = df_clean[col].mode()[0]
                        df_clean[col] = df_clean[col].fillna(mode_val)
            else:
                # Numeric, fill with mean
                if df_clean[col].isnull().any():
                    mean_val = df_clean[col].mean()
                    df_clean[col] = df_clean[col].fillna(mean_val)
        
        return df_clean

# --- Agent 2: The Viz Architect ---
class VizArchitect(GroqClient):
    def __init__(self, api_key):
        super().__init__(api_key)

    def generate_charts(self, df: pd.DataFrame):
        """
        Analyzes the dataframe and generates Plotly code for 4 distinct visualizations.
        Returns a list of JSON objects with title, description, and the figure object.
        """
        # Prepare metadata for the LLM
        columns = df.columns.tolist()
        dtypes = df.dtypes.astype(str).to_dict()
        head = df.head(3).to_string()
        
        prompt = f"""
        You are an expert Data Visualization Architect.
        Analyze the following dataset metadata:
        Columns: {columns}
        Data Types: {dtypes}
        Sample Data:
        {head}

        Your Task:
        Generate 4 DISTINCT and meaningful Plotly visualizations to create a comprehensive dashboard.
        1. Analyze the data to find trends, distributions, correlations, and categorical breakdowns.
        2. For EACH visualization:
           - Choose the best chart type (Line, Bar, Scatter, Pie, Box, Histogram, etc.).
           - Write Python code using Plotly Express (`px`) to create the chart.
           - The dataframe is named `df`.
           - The figure object must be named `fig1`, `fig2`, `fig3`, `fig4` respectively.
           - Create a "Story" (headline) and a "Description".

        Output Format:
        Return ONLY a valid JSON object with the following structure. Do not wrap in markdown code blocks.
        {{
            "charts": [
                {{
                    "story": "Headline for Chart 1",
                    "description": "Explanation 1",
                    "code": "fig1 = px.line(df, ...)"
                }},
                {{
                    "story": "Headline for Chart 2",
                    "description": "Explanation 2",
                    "code": "fig2 = px.bar(df, ...)"
                }},
                ... (total 4 charts)
            ]
        }}
        """

        response = self.get_completion(prompt, system_message="You are a JSON-speaking Data Visualization expert.")
        
        # Clean response if it contains markdown code blocks
        if "```json" in response:
            response = response.split("```json")[1].split("```")[0]
        elif "```" in response:
            response = response.split("```")[1].split("```")[0]
            
        results = []
        try:
            data = json.loads(response)
            charts = data.get('charts', [])
            
            base_vars = {'df': df, 'px': px, 'go': go}
            
            for i, chart in enumerate(charts):
                try:
                    # Create a fresh context for each chart to avoid variable pollution
                    local_vars = base_vars.copy()
                    
                    # Execute the code
                    exec(chart['code'], {}, local_vars)
                    
                    # Figure name is likely fig1, fig2, etc. or just fig if the LLM messed up. 
                    fig_name = f"fig{i+1}"
                    fig = local_vars.get(fig_name)
                    
                    # Fallback: if figN not found, check if 'fig' was used
                    if not fig:
                         fig = local_vars.get('fig')

                    if fig:
                        results.append({
                            "story": chart['story'],
                            "description": chart['description'],
                            "figure": fig
                        })
                except Exception as e:
                    print(f"Error generating chart {i+1}: {e}")
                    continue
            
            return results

        except Exception as e:
            print(f"Error parsing JSON: {e}")
            return []

# --- Agent 3: Talking Rabbitt (The Analyst) ---
class TalkingRabbit(GroqClient):
    def __init__(self, api_key):
        super().__init__(api_key)

    def ask_question(self, df: pd.DataFrame, question: str):
        """
        Converts natural language question to Pandas query, executes it, and synthesizes an answer.
        """
        columns = df.columns.tolist()
        dtypes = df.dtypes.astype(str).to_dict()
        head = df.head(3).to_string()

        prompt = f"""
        You are an expert Data Analyst named "Talking Rabbit".
        User Question: "{question}"

        Dataset Metadata:
        Columns: {columns}
        Data Types: {dtypes}
        Sample Data:
        {head}

        Your Task:
        1. Write a Python Pandas query to answer the question.
           - Assume the dataframe is named `df`.
           - Store the result in a variable named `result`.
           - The query should be a single executable line or block.
        2. Execute the query (I will do this part, you just provide the code).
        
        Output Format:
        Return ONLY the Python code. Do not wrap in markdown. Do not include print statements.
        Example: result = df[df['Category'] == 'A']['Sales'].sum()
        """

        code_response = self.get_completion(prompt, system_message="You are a Python Pandas coding expert. Output ONLY code.")
        
        # Clean code response
        code_response = code_response.replace("```python", "").replace("```", "").strip()

        try:
            local_vars = {'df': df}
            exec(code_response, {}, local_vars)
            result_val = local_vars.get('result')
            
            # Synthesize answer
            synthesis_prompt = f"""
            User Question: "{question}"
            Data Analysis Result: {result_val}
            
            Task: Provide a natural language answer to the user's question based on the result.
            Keep it professional, concise, and friendly.
            """
            answer = self.get_completion(synthesis_prompt, system_message="You are a helpful Data Analyst.")
            return answer, code_response
            
        except Exception as e:
            return f"I couldn't analyze that. Error: {e}", code_response
