import pandas as pd
from sqlalchemy import create_engine, text
from traindata import MyVanna
from config import DB_HOST, DB_NAME, DB_USER, DB_PASS, DB_PORT, OPENAI_API_KEY

def generate_complex_examples():
    """
    Generate complex SQL query examples to enhance Vanna's training.
    Each example includes a natural language question and its corresponding SQL query.
    """
    complex_examples = [
        # JOIN examples
        {
            "question": "What is the demand and revenue for each product type across all stores?",
            "sql": """
                SELECT 
                    product_type, 
                    SUM(demand) as total_demand, 
                    SUM(demand * revenue_per_unit) as total_revenue
                FROM demands
                GROUP BY product_type
                ORDER BY total_revenue DESC
            """
        },
        {
            "question": "What is the average processing cost per unit for each product type?",
            "sql": """
                SELECT 
                    product_type, 
                    AVG(cost_per_unit) as avg_cost_per_unit,
                    MIN(cost_per_unit) as min_cost,
                    MAX(cost_per_unit) as max_cost
                FROM processing
                GROUP BY product_type
                ORDER BY avg_cost_per_unit DESC
            """
        },
        
        # More complex JOIN between tables
        {
            "question": "What is the total demand value for each product type compared to the available processing capacity?",
            "sql": """
                WITH demand_summary AS (
                    SELECT 
                        product_type, 
                        SUM(demand) as total_demand,
                        SUM(demand * revenue_per_unit) as total_revenue_potential
                    FROM demands
                    GROUP BY product_type
                ),
                processing_summary AS (
                    SELECT 
                        product_type, 
                        SUM(capacity) as total_capacity,
                        AVG(cost_per_unit) as avg_cost_per_unit
                    FROM processing
                    GROUP BY product_type
                )
                SELECT 
                    d.product_type,
                    d.total_demand,
                    p.total_capacity,
                    CASE 
                        WHEN p.total_capacity >= d.total_demand THEN 'Sufficient Capacity'
                        ELSE 'Capacity Shortage'
                    END as capacity_status,
                    d.total_revenue_potential,
                    p.avg_cost_per_unit,
                    d.total_revenue_potential - (d.total_demand * p.avg_cost_per_unit) as estimated_profit
                FROM demand_summary d
                JOIN processing_summary p ON d.product_type = p.product_type
                ORDER BY estimated_profit DESC
            """
        },
        
        # Window functions
        {
            "question": "Rank stores by their total demand value and show what percentage of total demand each store represents",
            "sql": """
                WITH store_totals AS (
                    SELECT 
                        node_id as store, 
                        SUM(demand) as total_demand,
                        SUM(demand * revenue_per_unit) as total_value
                    FROM demands
                    GROUP BY node_id
                ),
                overall_total AS (
                    SELECT SUM(total_demand) as grand_total_demand
                    FROM store_totals
                )
                SELECT 
                    store,
                    total_demand,
                    total_value,
                    RANK() OVER (ORDER BY total_value DESC) as value_rank,
                    ROUND((total_demand * 100.0 / grand_total_demand), 2) as percentage_of_total_demand
                FROM store_totals, overall_total
                ORDER BY value_rank
            """
        },
        
        # Subqueries
        {
            "question": "Find products where demand exceeds the average demand for their product type",
            "sql": """
                SELECT 
                    d1.node_id,
                    d1.product_type,
                    d1.demand,
                    (
                        SELECT AVG(demand) 
                        FROM demands d2 
                        WHERE d2.product_type = d1.product_type
                    ) as avg_demand_for_type,
                    d1.demand - (
                        SELECT AVG(demand) 
                        FROM demands d2 
                        WHERE d2.product_type = d1.product_type
                    ) as demand_difference
                FROM demands d1
                WHERE d1.demand > (
                    SELECT AVG(demand) 
                    FROM demands d2 
                    WHERE d2.product_type = d1.product_type
                )
                ORDER BY demand_difference DESC
            """
        },
        
        # CASE statements and complex calculations
        {
            "question": "Categorize each store based on its GPU to CPU demand ratio and show total revenue potential",
            "sql": """
                WITH store_demands AS (
                    SELECT 
                        node_id as store,
                        SUM(CASE WHEN product_type = 'cpu' THEN demand ELSE 0 END) as cpu_demand,
                        SUM(CASE WHEN product_type = 'gpu' THEN demand ELSE 0 END) as gpu_demand,
                        SUM(demand * revenue_per_unit) as total_revenue
                    FROM demands
                    GROUP BY node_id
                )
                SELECT 
                    store,
                    cpu_demand,
                    gpu_demand,
                    ROUND(CAST(gpu_demand AS FLOAT) / NULLIF(cpu_demand, 0), 2) as gpu_to_cpu_ratio,
                    CASE 
                        WHEN gpu_demand = 0 THEN 'CPU Only'
                        WHEN cpu_demand = 0 THEN 'GPU Only'
                        WHEN gpu_demand > cpu_demand THEN 'GPU Heavy'
                        WHEN gpu_demand = cpu_demand THEN 'Balanced'
                        ELSE 'CPU Heavy'
                    END as store_category,
                    total_revenue
                FROM store_demands
                ORDER BY gpu_to_cpu_ratio DESC
            """
        },
        
        # Cross-table analysis
        {
            "question": "What's the cost efficiency of each processing node based on capacity and cost per unit?",
            "sql": """
                SELECT 
                    node_id,
                    node_type,
                    product_type,
                    capacity,
                    cost_per_unit,
                    ROUND(CAST(capacity AS FLOAT) / NULLIF(cost_per_unit, 0), 2) as efficiency_ratio,
                    RANK() OVER (PARTITION BY product_type ORDER BY CAST(capacity AS FLOAT) / NULLIF(cost_per_unit, 0) DESC) as efficiency_rank
                FROM processing
                ORDER BY product_type, efficiency_rank
            """
        },
        
        # UPDATE examples
        {
            "question": "Increase the demand for all CPU products by 15%",
            "sql": """
                UPDATE demands
                SET demand = demand * 1.15
                WHERE product_type = 'cpu'
            """
        },
        
        {
            "question": "Increase the revenue per unit for stores with high demand (over 600 units)",
            "sql": """
                UPDATE demands
                SET revenue_per_unit = revenue_per_unit * 1.1
                WHERE demand > 600
            """
        },
        
        # Custom aggregations
        {
            "question": "Calculate quartiles of cost per unit for each product type",
            "sql": """
                WITH product_costs AS (
                    SELECT 
                        product_type,
                        cost_per_unit,
                        NTILE(4) OVER (PARTITION BY product_type ORDER BY cost_per_unit) as quartile
                    FROM processing
                )
                SELECT 
                    product_type,
                    quartile,
                    MIN(cost_per_unit) as min_cost,
                    MAX(cost_per_unit) as max_cost,
                    AVG(cost_per_unit) as avg_cost
                FROM product_costs
                GROUP BY product_type, quartile
                ORDER BY product_type, quartile
            """
        }
    ]
    
    return complex_examples

def train_with_complex_examples():
    """
    Initialize Vanna and train it with complex examples.
    """
    # Initialize Vanna
    vn = MyVanna(config={
        'api_key': OPENAI_API_KEY,
        'model': 'gpt-4',
        'path': './vanna_chromadb'
    })
    
    # Connect to the database
    vn.connect_to_postgres(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        port=DB_PORT
    )
    
    # Generate complex examples
    examples = generate_complex_examples()
    
    # Train Vanna with each example
    print(f"Training Vanna with {len(examples)} complex examples...")
    for i, example in enumerate(examples):
        print(f"Training example {i+1}/{len(examples)}: {example['question']}")
        vn.train(question=example["question"], sql=example["sql"])
    
    print("Training with complex examples complete!")
    return vn

if __name__ == "__main__":
    train_with_complex_examples() 