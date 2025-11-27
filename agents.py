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
                        # Validate that the figure is JSON-serializable
                        try:
                            # Test serialization before adding to results
                            import plotly.io as pio
                            pio.to_json(fig, validate=False)
                            
                            results.append({
                                "story": chart['story'],
                                "description": chart['description'],
                                "figure": fig
                            })
                        except (TypeError, ValueError) as json_err:
                            print(f"Chart {i+1} serialization failed: {json_err}")
                            # Try multiple fix strategies
                            fixed = False
                            
                            # Strategy 1: Convert to dict and back
                            try:
                                fig_dict = fig.to_dict()
                                clean_fig = go.Figure(fig_dict)
                                pio.to_json(clean_fig, validate=False)
                                results.append({
                                    "story": chart['story'],
                                    "description": chart['description'],
                                    "figure": clean_fig
                                })
                                fixed = True
                                print(f"Chart {i+1} fixed with strategy 1")
                            except Exception:
                                pass
                            
                            # Strategy 2: Recreate with plotly express if strategy 1 failed
                            if not fixed:
                                try:
                                    # Try to re-execute the code with fresh context
                                    retry_vars = {'df': df, 'px': px, 'go': go, 'pd': pd}
                                    exec(chart['code'], {}, retry_vars)
                                    retry_fig = retry_vars.get(f"fig{i+1}") or retry_vars.get('fig')
                                    
                                    if retry_fig:
                                        # Update layout to ensure JSON compatibility
                                        retry_fig.update_layout(template="plotly_dark")
                                        pio.to_json(retry_fig, validate=False)
                                        results.append({
                                            "story": chart['story'],
                                            "description": chart['description'],
                                            "figure": retry_fig
                                        })
                                        fixed = True
                                        print(f"Chart {i+1} fixed with strategy 2")
                                except Exception as e2:
                                    print(f"Chart {i+1} strategy 2 failed: {e2}")
                            
                            # Strategy 3: Create a simple fallback chart
                            if not fixed:
                                try:
                                    # Create a simple text-based figure as fallback
                                    fallback_fig = go.Figure()
                                    fallback_fig.add_annotation(
                                        text=f"Chart rendering failed<br>{chart['story']}",
                                        xref="paper", yref="paper",
                                        x=0.5, y=0.5, showarrow=False,
                                        font=dict(size=14, color="white")
                                    )
                                    fallback_fig.update_layout(
                                        template="plotly_dark",
                                        height=300,
                                        showlegend=False
                                    )
                                    results.append({
                                        "story": chart['story'],
                                        "description": "Visualization could not be rendered. " + chart['description'],
                                        "figure": fallback_fig
                                    })
                                    print(f"Chart {i+1} using fallback")
                                except Exception as e3:
                                    print(f"Chart {i+1} all strategies failed: {e3}")
                                    continue
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
        self.conversation_history = []

    def ask_question(self, df: pd.DataFrame, question: str, conversation_history=None):
        """
        Converts natural language question to analysis, with conversation memory.
        Can generate text answers OR visualizations based on the question.
        """
        if conversation_history is None:
            conversation_history = self.conversation_history
            
        columns = df.columns.tolist()
        dtypes = df.dtypes.astype(str).to_dict()
        head = df.head(3).to_string()
        
        # Build conversation context
        context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation_history[-5:]])  # Last 5 messages

        # First, determine if user wants a visualization
        intent_prompt = f"""
        Analyze this user question and determine if they want a VISUALIZATION or just a TEXT answer.
        
        User Question: "{question}"
        
        Return ONLY one word: "VISUALIZATION" or "TEXT"
        
        Keywords for visualization: chart, plot, graph, visualize, show me, display, draw
        """
        
        intent = self.get_completion(intent_prompt, system_message="You are a classification expert.").strip().upper()
        
        if "VISUALIZATION" in intent or "VIZ" in intent:
            # Generate visualization
            return self._generate_visualization(df, question, context, columns, dtypes, head)
        else:
            # Generate text answer
            return self._generate_text_answer(df, question, context, columns, dtypes, head)
    
    def _generate_text_answer(self, df, question, context, columns, dtypes, head):
        """Generate a text-based answer with Pandas code."""
        prompt = f"""
        You are an expert Data Analyst named "Talking Rabbit".
        
        Conversation History:
        {context}
        
        Current User Question: "{question}"

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
        2. Consider the conversation history for context.
        
        Output Format:
        Return ONLY the Python code. Do not wrap in markdown. Do not include print statements.
        Example: result = df[df['Category'] == 'A']['Sales'].sum()
        """

        code_response = self.get_completion(prompt, system_message="You are a Python Pandas coding expert. Output ONLY code.")
        
        # Clean code response
        code_response = code_response.replace("```python", "").replace("```", "").strip()

        try:
            local_vars = {'df': df, 'pd': pd}
            exec(code_response, {}, local_vars)
            result_val = local_vars.get('result')
            
            # Synthesize answer
            synthesis_prompt = f"""
            Conversation History:
            {context}
            
            User Question: "{question}"
            Data Analysis Result: {result_val}
            
            Task: Provide a natural language answer to the user's question based on the result.
            Keep it professional, concise, and friendly. Reference previous conversation if relevant.
            """
            answer = self.get_completion(synthesis_prompt, system_message="You are a helpful Data Analyst.")
            
            return {
                "type": "text",
                "answer": answer,
                "code": code_response,
                "figure": None
            }
            
        except Exception as e:
            return {
                "type": "text",
                "answer": f"I couldn't analyze that. Error: {e}",
                "code": code_response,
                "figure": None
            }
    
    def _generate_visualization(self, df, question, context, columns, dtypes, head):
        """Generate a visualization based on the question."""
        prompt = f"""
        You are an expert Data Visualization specialist.
        
        Conversation History:
        {context}
        
        Current User Question: "{question}"
        
        Dataset Metadata:
        Columns: {columns}
        Data Types: {dtypes}
        Sample Data:
        {head}

        Your Task:
        Generate Python code using Plotly Express (`px`) to create the requested visualization.
        - The dataframe is named `df`.
        - The figure object must be named `fig`.
        - Choose the appropriate chart type based on the question.
        - Add proper titles and labels.
        
        Output Format:
        Return ONLY the Python code. Do not wrap in markdown.
        Example: fig = px.bar(df, x='Category', y='Sales', title='Sales by Category')
        """

        code_response = self.get_completion(prompt, system_message="You are a Plotly visualization expert. Output ONLY code.")
        
        # Clean code response
        code_response = code_response.replace("```python", "").replace("```", "").strip()

        try:
            local_vars = {'df': df, 'px': px, 'go': go, 'pd': pd}
            exec(code_response, {}, local_vars)
            fig = local_vars.get('fig')
            
            if fig:
                # Validate JSON serialization
                try:
                    import plotly.io as pio
                    pio.to_json(fig, validate=False)
                except (TypeError, ValueError):
                    # Try to clean the figure
                    fig_dict = fig.to_dict()
                    fig = go.Figure(fig_dict)
                
                # Generate description
                desc_prompt = f"""
                User asked: "{question}"
                A visualization was created.
                
                Provide a brief 1-sentence description of what the chart shows.
                """
                description = self.get_completion(desc_prompt, system_message="You are concise.")
                
                return {
                    "type": "visualization",
                    "answer": description,
                    "code": code_response,
                    "figure": fig
                }
            else:
                return {
                    "type": "text",
                    "answer": "I couldn't generate the visualization. Please try rephrasing your request.",
                    "code": code_response,
                    "figure": None
                }
                
        except Exception as e:
            return {
                "type": "text",
                "answer": f"I couldn't create the visualization. Error: {e}",
                "code": code_response,
                "figure": None
            }

